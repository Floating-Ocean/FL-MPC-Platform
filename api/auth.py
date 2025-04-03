from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Blueprint, request, jsonify, session
from models import Model, db, User, TrainingRecord
from lib.train.session import open_session, check_classify_acc, get_available_models
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


# 使用 Manager 创建共享字典
global_training_status = {}


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
    def current_session():
        if not current_user.is_authenticated:
            return jsonify({'msg': "Unauthorized!"}), 403
        return jsonify({'message': 'User is logged in', 'user_id': current_user.id, 'username': current_user.username}), 200

    @auth_bp.route('/start_training', methods=['POST'])
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

        # 使用 Manager 创建共享字典
        training_status = Manager().dict()
        global_training_status[str(task_id)] = training_status

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
    @auth_bp.route('/get_training_progress', methods=['GET'])
    @login_required
    def get_training_progress():
        # 获取当前用户的训练记录
        training_records = TrainingRecord.query.filter_by(user_id=current_user.id, completed=False).all()
        
        if not training_records:
            return jsonify({'message': '当前用户无任务在进行'}), 200

        # 假设每个用户只有一个未完成的任务，返回第一个未完成的任务
        training_record = training_records[0]
        task_id = training_record.model.name.split('_')[-1]  # 假设 model.name 格式为 model_<task_id>
        training_status = global_training_status.get(str(task_id), {})

        return jsonify({
            'task_id': task_id,
            'completed': training_status.get('completed', False),
            'loss_list': training_status.get('loss_list', []),
            'acc_list': training_status.get('acc_list', [])
        }), 200

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