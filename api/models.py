from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    models = db.relationship('Model', backref='user', lazy=True)

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_directory = db.Column(db.String(255), nullable=False)
    is_user_uploaded = db.Column(db.Boolean, default=False)
    training_records = db.relationship('TrainingRecord', backref='model', lazy=True)

class TrainingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    loss_list = db.Column(db.JSON, nullable=False)
    acc_list = db.Column(db.JSON, nullable=False)
    train_acc = db.Column(db.Float, nullable=False)
    test_acc = db.Column(db.Float, nullable=False)
