import json
import os
import uuid
from multiprocessing import Manager, Process

from flask import Blueprint, request, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from lib.train.session import open_session, check_classify_acc, get_available_models
from models import Model, db, User, TrainingRecord

auth_bp = Blueprint('auth', __name__)

# 初始化 LoginManager
login_manager = LoginManager()

# 定义 user_loader 回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

training_status = {}
user_tasks = {}

def allowed_file(filename):
    # 验证文件合法性的逻辑
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def register_routes(app):
    @app.route('/register', methods=['POST'])
    def register():
        data = request.json
        # 注册用户的逻辑
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return None
        user = User()
        user.username = username
        user.password = password
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json

        # 输入验证
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': 'Invalid input', 'error': 'Username and password are required'}), 400

        username = data.get('username')
        password = data.get('password')

        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message': 'Invalid credentials', 'error': 'User not found'}), 401

        # 验证密码
        if user.password != password:
            return jsonify({'message': 'Invalid credentials', 'error': 'Incorrect password'}), 401

        # 登录用户
        if not login_user(user):
            return jsonify({'message': 'Login Failed', 'error': 'Login Failed'}), 500

        session.modified = True  # 强制会话更新
        return jsonify({'message': 'Logged in successfully', 'user_id': user.id}), 200

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200

    @app.route('/current_session', methods=['GET'])
    @login_required
    def current_session():
        return jsonify({'message': 'User is logged in', 'user_id': current_user.id, 'username': current_user.username}), 200

    @app.route('/start_training', methods=['POST'])
    @login_required
    def start_training():
        data = request.json
        dataset_type = data.get('dataset_type')
        epochs = data.get('epochs')
        if not dataset_type or not epochs:
            return jsonify({'message': 'Invalid input'}), 400

        task_id = uuid.uuid4()
        user_tasks[current_user.id] = task_id

        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(task_id))
        os.makedirs(output_dir, exist_ok=True)

        p = Process(target=open_session, args=(task_id, epochs, dataset_type, output_dir, training_status['dict']))
        p.start()

        return jsonify({'message': 'Training started', 'task_id': str(task_id)}), 200

    @app.route('/get_training_progress', methods=['GET'])
    @login_required
    def get_training_progress():
        # 获取当前用户的训练记录
        task_id = user_tasks.get(current_user.id)
        if not task_id:
            return jsonify({'message': 'No running task'}), 200

        current_status = training_status['dict'].get(task_id, {
            'status': 'INITIALIZING',
            'data': None
        })

        return jsonify({
            'message': 'Task running',
            'status': current_status.get('status', 'INITIALIZING'),
            'data': current_status.get('data', None)
        }), 200

    @app.route('/train_finish', methods=['GET'])
    @login_required
    def train_finish():
        # 通知后端训练结束，存储记录
        task_id = user_tasks.get(current_user.id)
        if not task_id:
            return jsonify({'message': 'No running task'}), 400

        current_status = training_status['dict'].get(task_id, {
            'status': 'INITIALIZING',
            'data': {}
        })
        if current_status['status'] != 'FINISHED':
            return jsonify({'message': 'Task still running'}), 400

        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(task_id))
        os.makedirs(output_dir, exist_ok=True)

        # todo: 可以搞一个模型命名
        model = Model(name=f"model_{task_id}", user_id=current_user.id, file_directory=output_dir)
        db.session.add(model)
        db.session.commit()

        record = TrainingRecord(model_id=model.id,
                                loss_list=json.dumps(current_status['data']['loss_trains']),
                                acc_list=json.dumps(current_status['data']['acc_trains']),
                                test_acc=current_status['data']['test_acc'],
                                train_acc=current_status['data']['train_acc'])
        db.session.add(record)
        db.session.commit()

        return jsonify({'message': 'Record saved'}), 200

    @app.route('/get_last_record', methods=['GET'])
    @login_required
    def get_last_record():
        # 获取用户的最后一次训练记录
        record = (TrainingRecord.query
                  .join(Model, TrainingRecord.model_id == Model.id)
                  .filter(Model.user_id == current_user.id)
                  .order_by(TrainingRecord.id.desc())
                  .first())
        if not record:
            return jsonify({'message': 'No record yet'}), 404

        return jsonify({'message': 'Record found',
                        'loss_list': json.loads(record.loss_list),
                        'acc_list': json.loads(record.acc_list),
                        'test_acc': record.test_acc,
                        'train_acc': record.train_acc}), 200

    @app.route('/get_models', methods=['GET'])
    @login_required
    def get_models():
        models = get_available_models()
        return jsonify({'message': 'Models available', 'models': models}), 200

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