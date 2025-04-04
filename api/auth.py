import json
import os
import re
import uuid
from multiprocessing import Manager, Process

import unicodedata
from flask import Blueprint, request, jsonify, session, send_file, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from lib.train.session import open_session, check_classify_acc, get_available_datasets
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

        p = Process(target=open_session, args=(task_id, epochs, dataset_type, app.config['DATASET_FOLDER'],
                                               output_dir, training_status['dict']))
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

        user_tasks[current_user.id] = None  # 标记当前用户训练进程确认已结束

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

        return jsonify({'message': 'Record found', 'model_id': record.model_id,
                        'loss_list': json.loads(record.loss_list), 'acc_list': json.loads(record.acc_list),
                        'test_acc': record.test_acc, 'train_acc': record.train_acc}), 200

    @app.route('/get_datasets', methods=['GET'])
    @login_required
    def get_datasets():
        datasets = get_available_datasets()
        return jsonify({'message': 'Datasets available', 'datasets': datasets}), 200

    @app.route('/get_models', methods=['GET'])
    @login_required
    def get_models():
        models = (Model.query
                  .filter(Model.user_id == current_user.id)
                  .order_by(Model.id.desc()).all())
        if not models:
            return jsonify({'message': 'No models yet'}), 400

        response_models = [{'id': model.id, 'name': model.name} for model in models]
        return jsonify({'message': 'Models available', 'models': response_models}), 200

    @app.route('/download_model/<string:model_id>', methods=['GET'])
    @login_required
    def download_model(model_id: str):
        model = Model.query.filter(Model.id == model_id).one()
        if not model:
            return jsonify({'message': 'No such model'}), 400

        model_path = os.path.join(model.file_directory, f"{model.file_directory.split(os.path.sep)[-1]}.pth")
        if not os.path.isfile(model_path):
            return jsonify({'message': 'No such model file'}), 404

        response = make_response(send_file(
            path_or_file=model_path,
            as_attachment=True,
            download_name=f"{model.name}.pth"
        ))
        response.headers.extend({"Access-Control-Expose-Headers": "Content-Disposition"})

        return response

    @app.route('/upload_model', methods=['POST'])
    @login_required
    def upload_model():
        if 'file' not in request.files:
            return jsonify({'message': 'No file uploaded'}), 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'message': 'Invalid payload'}), 400

        filename = secure_filename(uploaded_file.filename)
        print(uploaded_file.filename, filename)
        if '.' in filename and filename.rsplit('.', 1)[1].lower() != 'pth':
            return jsonify({'message': 'Invalid file suffix'}), 400

        task_id = uuid.uuid4()
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(task_id))
        os.makedirs(output_dir, exist_ok=True)

        model_path = os.path.join(output_dir, f"{task_id}.pth")
        uploaded_file.save(model_path)

        model = Model(name=filename.removesuffix('.pth'), user_id=current_user.id, file_directory=output_dir,
                      is_user_uploaded=True)
        db.session.add(model)
        db.session.commit()

        return jsonify({'message': 'Model uploaded successfully'}), 200

    @app.route('/test_accuracy', methods=['POST'])
    @login_required
    def test_accuracy():
        if 'file' not in request.files:
            return jsonify({'message': 'No file uploaded'}), 400

        uploaded_file = request.files['file']
        model_id = request.form.get('model_id')

        if not model_id or uploaded_file.filename == '':
            return jsonify({'message': 'Invalid payload'}), 400

        if uploaded_file.mimetype not in ['image/jpeg', 'image/png']:
            return jsonify({'message': 'Invalid file mimetype'}), 400

        # 临时存储目录
        temp_dir = app.config['TEMP_FOLDER']
        os.makedirs(temp_dir, exist_ok=True)

        filename = secure_filename(uploaded_file.filename)
        temp_filename = str(uuid.uuid4()) + '_' + filename
        temp_path = os.path.join(temp_dir, temp_filename)
        uploaded_file.save(temp_path)

        model = Model.query.get(model_id)
        if not model:
            return jsonify({'message': 'Model not found'}), 404

        model_path = os.path.join(model.file_directory, f"{model.file_directory.split(os.path.sep)[-1]}.pth")
        acc_dict = Manager().dict()
        p = Process(target=check_classify_acc, args=(model_path, temp_path, app.config['DATASET_FOLDER'], acc_dict))
        p.start()
        p.join()

        if 'result' in acc_dict:
            return jsonify({'message': 'Prediction ok', 'result': acc_dict['result']}), 200
        else:
            return jsonify({'message': 'Prediction failed'}), 500


def secure_filename(filename: str) -> str:
    """Adapted from werkzeug/utils.py."""
    _filename_ascii_add_strip_re = re.compile(r'[^A-Za-z0-9_\u4E00-\u9FBF\u3040-\u30FF\u31F0-\u31FF.-]')
    _windows_device_files = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(10)),
        *(f"LPT{i}" for i in range(10)),
    }
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("utf-8", "ignore").decode("utf-8")

    for sep in os.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_add_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    if (
            os.name == "nt"
            and filename
            and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename