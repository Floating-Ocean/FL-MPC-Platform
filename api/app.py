# app.py
import os
import shutil
from multiprocessing import Manager

from flask import Flask
from flask_cors import CORS

from auth import login_manager, register_routes, training_status
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    training_status['manager'] = Manager()
    training_status['dict'] = training_status['manager'].dict()

    temp_dir, upload_dir = app.config['TEMP_FOLDER'], app.config['UPLOAD_FOLDER']
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    with app.app_context():
        db.create_all()

    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)