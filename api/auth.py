# auth.py
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Blueprint, request, jsonify
import threading
from models import Model, db, User
from lib.main import solve  # 导入solve函数

auth_bp = Blueprint('auth', __name__)

# 初始化 LoginManager
login_manager = LoginManager()

def register_user(data):
    # 注册用户的逻辑
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return None
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def login_user_func(data):
    # 登录用户的逻辑
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return user
    return None

def register_routes(app):
    @app.route('/register', methods=['POST'])
    def register():
        data = request.json
        user = register_user(data)
        return jsonify({'message': 'User registered successfully'}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        user = login_user_func(data)
        if user:
            return jsonify({'message': 'Logged in successfully'}), 200
        return jsonify({'message': 'Invalid credentials'}), 401

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200

    @app.route('/start_training', methods=['POST'])
    @login_required
    def start_training():
        data = request.json
        dataset_type = data['dataset_type']
        epochs = data['epochs']
        # 启动训练任务
        threading.Thread(target=solve).start()  # 调用main.py中的solve函数
        return jsonify({'message': 'Training started'}), 200

    @app.route('/get_training_progress', methods=['GET'])
    @login_required
    def get_training_progress():
        user = current_user
        if user and user.models:
            model = user.models[0]
            if model.training_records:
                training_record = model.training_records[-1]
                return jsonify({
                    'completed': training_record.completed,
                    'loss_list': json.loads(training_record.loss_list) if training_record.loss_list else [],
                    'acc_list': json.loads(training_record.acc_list) if training_record.acc_list else []
                }), 200
        return jsonify({'message': 'No training in progress'}), 404

    @app.route('/upload_model', methods=['POST'])
    @login_required
    def upload_model():
        file = request.files['model']
        # 验证模型文件合法性
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_model = Model(name=filename, user_id=current_user.id, file_directory=os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.session.add(new_model)
            db.session.commit()
            return jsonify({'message': 'Model uploaded successfully'}), 200
        return jsonify({'message': 'Invalid file'}), 400

    @app.route('/predict', methods=['POST'])
    @login_required
    def predict():
        file = request.files['image']
        model_id = request.form['model_id']
        # 使用模型进行预测
        result = predict_image(file, model_id)
        return jsonify({'result': result}), 200

    @app.route('/test_accuracy', methods=['POST'])
    @login_required
    def test_accuracy():
        dataset = request.json['dataset']
        # 计算模型准确度
        accuracy = calculate_accuracy(dataset)
        return jsonify({'accuracy': accuracy}), 200