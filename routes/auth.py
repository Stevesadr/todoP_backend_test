from flask import Blueprint,request,jsonify
from db import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask import current_app

from utils import token_required,send_verification_email
import random

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        if user.is_verified:
            return jsonify({'message': 'User already exists'}), 409
        else:

            new_code = str(random.randint(100000, 999999))
            user.verification_code = new_code
            db.session.commit()

            send_verification_email(email, new_code)

            return jsonify({'message': 'You have already registered but not verified. A new code has been sent.'}), 202


    hashed_password = generate_password_hash(password)
    verification_code = str(random.randint(100000, 999999))

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        is_verified=False,
        verification_code=verification_code
    )

    db.session.add(new_user)
    db.session.commit()

    send_verification_email(email, verification_code)

    return jsonify({
        'message': 'User registered. Please check your email to verify.',
        'email':email
    }), 201

    # token = jwt.encode({
    #     'user_id': new_user.id,
    #     'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    # } , current_app.config['SECRET_KEY'], algorithm='HS256')
    #
    # return jsonify({
    #     'message': 'User registered successfully',
    #     'token': token
    # }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    if not user.is_verified:
        return jsonify({'message': 'Account not verified'}), 403

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'],algorithm='HS256' )

    return jsonify({'token': token}), 200

@auth_bp.route('/user' , methods=['GET'])
@token_required
def get_user_info(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }),201

@auth_bp.route('/verify', methods=['POST'])
def verify_user():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.is_verified:
        return jsonify({'message': 'User already verified'}), 400

    if user.verification_code != code:
        return jsonify({'message': 'Invalid verification code'}), 401

    user.is_verified = True
    user.verification_code = None
    db.session.commit()

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Verification successful', 'token': token}), 200