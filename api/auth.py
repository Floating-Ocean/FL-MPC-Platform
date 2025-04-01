# auth.py
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Blueprint, request, jsonify, json
import threading
from models import Model, db, User, TrainingRecord
from lib.session import open_session, check_classify_acc
from multiprocessing import Manager, Process
import uuid
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

# 初始化 LoginManager
login_manager = LoginManager()

# 定义 user_loader 回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

def allowed_file(filename):
    # 验证文件合法性的逻辑
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def predict_image(file, model_id):
    # 使用模型进行预测的逻辑
    # 这里假设有一个函数 predict_image 实现了预测逻辑
    pass

def calculate_accuracy(dataset):
    # 计算模型准确度的逻辑
    # 这里假设有一个函数 calculate_accuracy 实现了准确度计算逻辑
    pass

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
        dataset_type = data.get('dataset_type')
        epochs = data.get('epochs')
        if not dataset_type or not epochs:
            return jsonify({'message': 'Invalid input'}), 400

        task_id = uuid.uuid4()
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(task_id))
        os.makedirs(output_dir, exist_ok=True)

        training_status = Manager().dict()
        p = Process(target=open_session, args=(task_id, epochs, dataset_type, output_dir, training_status))
        p.start()

        # 保存进程信息以便后续查询
        if current_user.models:
            model = current_user.models[0]
        else:
            model = Model(name=f"model_{task_id}", user_id=current_user.id, file_directory=output_dir)
            db.session.add(model)
            db.session.commit()

        training_record = TrainingRecord(model_id=model.id, completed=False)
        db.session.add(training_record)
        db.session.commit()

        return jsonify({'message': 'Training started', 'task_id': str(task_id)}), 200

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
        data = request.json
        model_id = data.get('model_id')
        img_path = data.get('img_path')

        if not model_id or not img_path:
            return jsonify({'message': 'Invalid input'}), 400

        model = Model.query.get(model_id)
        if not model:
            return jsonify({'message': 'Model not found'}), 404

        acc_dict = Manager().dict()
        p = Process(target=check_classify_acc, args=(model.file_directory, img_path, acc_dict))
        p.start()
        p.join()

        if 'result' in acc_dict:
            return jsonify({'result': acc_dict['result']}), 200
        else:
            return jsonify({'message': 'Prediction failed'}), 500