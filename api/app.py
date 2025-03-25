from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# 配置 CORS
CORS(app, supports_credentials=True)
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
)
Session(app)

# 配置 MySQL 连接
db_config = {
    'host': '192.168.241.182',
    'user': 'root',
    'password': 'a123.',
    'database': 'reviewer',
    'connect_timeout': 60  # 增加连接超时设置
}


def get_db_connection():
    attempts = 0
    while attempts < 3:  # 尝试重连三次
        try:
            return mysql.connector.connect(**db_config)
        except mysql.connector.errors.OperationalError as e:
            if e.errno == 2013:  # Lost connection to MySQL server during query
                time.sleep(2)  # 等待 2 秒后重试
                attempts += 1
            else:
                raise
    raise mysql.connector.errors.OperationalError("Failed to connect to the database after multiple attempts")


# 管理员验证装饰器
def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"msg": "Unauthorized! Please log in."}), 403
        if not session.get('is_admin', False):  # 检查用户是否为管理员
            return jsonify({"msg": "Admin privileges required!"}), 403
        return f(*args, **kwargs)

    # 将包装函数的名称改为原函数的名称，避免视图名称冲突
    wrapper.__name__ = f.__name__
    return wrapper


@app.before_request
def before_request():
    global db
    db = get_db_connection()


@app.teardown_request
def teardown_request(exception):
    db.close()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return jsonify({"msg": "Welcome to the home page!"})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = generate_password_hash(data['password'])
    email = data['email']

    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO users (UserName, Passwordhash, Email) VALUES (%s, %s, %s)", (username, password, email))
    db.commit()

    return jsonify({"msg": "Registration successful!"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE UserName = %s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user['Passwordhash'], password):
        session['user_id'] = user['UserID']
        session['username'] = user['UserName']
        session['is_admin'] = user['UserID'] == 1  # 只有 UserID 为 1 的用户是管理员
        return jsonify({"msg": "Login successful!"}), 200
    else:
        return jsonify({"msg": "Invalid credentials!"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('username', None)
    return jsonify({"msg": "Logged out successfully!"}), 200


@app.route('/data', methods=['GET'])
def admin():
    # 确保用户已登录
    if 'user_id' not in session:
        return jsonify({"msg": "Unauthorized! Please login."}), 403
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    cursor.execute("SELECT * FROM music")
    music = cursor.fetchall()
    return jsonify({"books": books, "movies": movies, "music": music}), 200


@app.route('/add_review', methods=['POST'])
def add_review():
    if not session.get('user_id'):
        return jsonify({"msg": "Unauthorized!"}), 403

    data = request.get_json()
    content_type = data['content_type']
    content_id = data['content_id']
    rating = data['rating']
    comment = data['comment']
    user_id = session['user_id']

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO reviews (UserID, ContentType, ContentID, Rating, Comment, CreatedAt) VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, content_type, content_id, rating, comment, created_at)
    )
    db.commit()

    return jsonify({"msg": "Review added successfully!"}), 201


@app.route('/reviews/<content_type>/<int:content_id>', methods=['GET'])
def get_reviews(content_type, content_id):
    content_query = None
    review_query = None

    if content_type == 'Book':
        content_query = "SELECT Title AS ContentName FROM books WHERE BookID = %s"
        review_query = """
            SELECT r.ReviewID, r.Rating, r.Comment, r.CreatedAt, r.UserID, u.UserName
            FROM reviews r
            JOIN users u ON r.UserID = u.UserID
            WHERE r.ContentType = 'Book' AND r.ContentID = %s
        """
    elif content_type == 'Movie':
        content_query = "SELECT Title AS ContentName FROM movies WHERE MovieID = %s"
        review_query = """
            SELECT r.ReviewID, r.Rating, r.Comment, r.CreatedAt, r.UserID, u.UserName
            FROM reviews r
            JOIN users u ON r.UserID = u.UserID
            WHERE r.ContentType = 'Movie' AND r.ContentID = %s
        """
    elif content_type == 'Music':
        content_query = "SELECT Title AS ContentName FROM music WHERE MusicID = %s"
        review_query = """
            SELECT r.ReviewID, r.Rating, r.Comment, r.CreatedAt, r.UserID, u.UserName
            FROM reviews r
            JOIN users u ON r.UserID = u.UserID
            WHERE r.ContentType = 'Music' AND r.ContentID = %s
        """
    else:
        return jsonify({"msg": "Invalid content type!"}), 400

    cursor = db.cursor(dictionary=True)
    cursor.execute(content_query, (content_id,))
    content = cursor.fetchone()

    if not content:
        return jsonify({"msg": "Content not found!"}), 404

    cursor.execute(review_query, (content_id,))
    reviews = cursor.fetchall()

    result = {
        "ContentName": content["ContentName"],
        "Reviews": reviews if reviews else []
    }

    return jsonify(result), 200


@app.route('/add_book', methods=['PUT'])
def add_book():
    if not session.get('is_admin'):
        return jsonify({"msg": "Unauthorized!"}), 403
    data = request.get_json()
    title = data['Title']
    author = data['Author']
    genre = data['Genre']
    publication_year = data['PublicationYear']
    isbn = data['ISBN']
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO books (Title, Author, Genre, PublicationYear, ISBN) VALUES (%s, %s, %s, %s, %s)",
                   (title, author, genre, publication_year, isbn))
    db.commit()
    return jsonify({"msg": "Book added successfully!"}), 201


@app.route('/add_movie', methods=['PUT'])
def add_movie():
    if not session.get('is_admin'):
        return jsonify({"msg": "Unauthorized!"}), 403
    data = request.get_json()
    title = data['Title']
    director = data['Director']
    genre = data['Genre']
    release_year = data['ReleaseYear']
    duration = data['Duration']
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO movies (Title, Director, Genre, ReleaseYear, Duration) VALUES (%s, %s, %s, %s, %s)",
                   (title, director, genre, release_year, duration))
    db.commit()
    return jsonify({"msg": "Movie added successfully!"}), 201


@app.route('/add_music', methods=['PUT'])
def add_music():
    if not session.get('is_admin'):
        return jsonify({"msg": "Unauthorized!"}), 403
    data = request.get_json()
    title = data['Title']
    artist = data['Artist']
    album = data['Album']
    release_year = data['ReleaseYear']
    genre = data['Genre']
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO music (Title, Artist, Album, ReleaseYear, Genre) VALUES (%s, %s, %s, %s, %s)",
                   (title, artist, album, release_year, genre))
    db.commit()
    return jsonify({"msg": "Music added successfully!"}), 201


@app.route('/edit_book', methods=['PUT'])
@admin_required
def edit_book():
    data = request.json
    book_id = data.get('BookID')
    title = data.get('Title')
    author = data.get('Author')
    genre = data.get('Genre')
    publication_year = data.get('PublicationYear')
    isbn = data.get('ISBN')

    if not book_id or not title or not author:
        return jsonify({"msg": "BookID, Title, and Author are required!"}), 400

    cursor = db.cursor()
    cursor.execute("""
        UPDATE books 
        SET Title = %s, Author = %s, Genre = %s, PublicationYear = %s, ISBN = %s 
        WHERE BookID = %s
    """, (title, author, genre, publication_year, isbn, book_id))
    db.commit()

    return jsonify({"msg": "Book updated successfully!"}), 200


@app.route('/delete_book', methods=['POST'])
@admin_required
def delete_book():
    data = request.json
    book_id = data.get('BookID')

    if not book_id:
        return jsonify({"msg": "BookID is required!"}), 400

    cursor = db.cursor()
    cursor.execute("SELECT * FROM books WHERE BookID = %s", (book_id,))
    book = cursor.fetchone()

    if not book:
        return jsonify({"msg": "Book not found!"}), 404

    cursor.execute("DELETE FROM books WHERE BookID = %s", (book_id,))
    db.commit()

    return jsonify({"msg": "Book deleted successfully!"}), 200


@app.route('/edit_movie', methods=['PUT'])
@admin_required
def edit_movie():
    data = request.json
    movie_id = data.get('MovieID')
    title = data.get('Title')
    director = data.get('Director')
    genre = data.get('Genre')
    release_year = data.get('ReleaseYear')
    duration = data.get('Duration')

    if not movie_id or not title or not director:
        return jsonify({"msg": "MovieID, Title, and Director are required!"}), 400

    cursor = db.cursor()
    cursor.execute("""
        UPDATE movies 
        SET Title = %s, Director = %s, Genre = %s, ReleaseYear = %s, Duration = %s 
        WHERE MovieID = %s
    """, (title, director, genre, release_year, duration, movie_id))
    db.commit()

    return jsonify({"msg": "Movie updated successfully!"}), 200


@app.route('/delete_movie', methods=['POST'])
@admin_required
def delete_movie():
    data = request.json
    movie_id = data.get('MovieID')

    if not movie_id:
        return jsonify({"msg": "MovieID is required!"}), 400

    cursor = db.cursor()
    cursor.execute("SELECT * FROM movies WHERE MovieID = %s", (movie_id,))
    movie = cursor.fetchone()

    if not movie:
        return jsonify({"msg": "Movie not found!"}), 404

    cursor.execute("DELETE FROM movies WHERE MovieID = %s", (movie_id,))
    db.commit()

    return jsonify({"msg": "Movie deleted successfully!"}), 200


@app.route('/edit_music', methods=['PUT'])
@admin_required
def edit_music():
    data = request.json
    music_id = data.get('MusicID')
    title = data.get('Title')
    artist = data.get('Artist')
    album = data.get('Album')
    release_year = data.get('ReleaseYear')
    genre = data.get('Genre')

    if not music_id or not title or not artist:
        return jsonify({"msg": "MusicID, Title, and Artist are required!"}), 400

    cursor = db.cursor()
    cursor.execute("""
        UPDATE music 
        SET Title = %s, Artist = %s, Album = %s, ReleaseYear = %s, Genre = %s 
        WHERE MusicID = %s
    """, (title, artist, album, release_year, genre, music_id))
    db.commit()

    return jsonify({"msg": "Music updated successfully!"}), 200


@app.route('/delete_music', methods=['POST'])
@admin_required
def delete_music():
    data = request.json
    music_id = data.get('MusicID')

    if not music_id:
        return jsonify({"msg": "MusicID is required!"}), 400

    cursor = db.cursor()
    cursor.execute("SELECT * FROM music WHERE MusicID = %s", (music_id,))
    music = cursor.fetchone()

    if not music:
        return jsonify({"msg": "Music not found!"}), 404

    cursor.execute("DELETE FROM music WHERE MusicID = %s", (music_id,))
    db.commit()

    return jsonify({"msg": "Music deleted successfully!"}), 200


@app.route('/current_session', methods=['GET'])
def current_session():
    if 'user_id' not in session:
        return jsonify({"msg": "Unauthorized!"}), 403
    user_id = session.get('user_id', 404)
    username = session.get('username', '404')
    is_admin = session.get('is_admin', False)
    return jsonify({'userId': user_id, 'username': username, 'isAdmin': is_admin}), 200


if __name__ == '__main__':
    app.run(debug=True)
