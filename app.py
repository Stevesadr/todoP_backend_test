from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from db import db
from models import User,Todo
import os

from routes.auth import auth_bp
from routes.todos import todos_bp

app = Flask(__name__)
CORS(app)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "supersecretkey")

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(todos_bp, url_prefix="/todos")


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
