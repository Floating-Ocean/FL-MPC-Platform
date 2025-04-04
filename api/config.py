class Config:
    SECRET_KEY = '1c1b7eafa52997ab696e44c50d9f24f5'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flask_db:flask_db@localhost/flask_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    TEMP_FOLDER = 'temp'
    DATASET_FOLDER = 'F:\\MachineLearning\\dataset'  # 需修改为自己的路径
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'