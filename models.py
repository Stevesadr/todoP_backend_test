from email.policy import default

from sqlalchemy.orm import backref

from db import db
from datetime import datetime,date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)

    todos = db.relationship("Todo" , backref="user" ,lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    task_date = db.Column(db.Date, nullable=False , default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)