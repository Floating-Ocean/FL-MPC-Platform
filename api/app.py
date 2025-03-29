# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models import db
from auth import login_manager, register_routes
from lib.main import solve  # 导入solve函数

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)

    # 添加训练路由
    @app.route('/train')
    def train():
        solve()
        return "训练已启动"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)