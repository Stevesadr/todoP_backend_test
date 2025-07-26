from functools import wraps

import requests
from flask import request, jsonify, current_app
import jwt


RESEND_API_KEY = 're_SnvoSJf3_HUUWnkZP7XisbexnwBts3q46'  # 👈 API Key خودت
FROM_EMAIL = 'verify@todopro.sbs'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
            else:
                return jsonify({'message': 'Authorization header is malformed'}), 401
        else:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id', None)
            if user_id is None:
                return jsonify({'message': 'Token payload missing user_id'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401

        kwargs['user_id'] = user_id
        return f(*args, **kwargs)

    return decorated

def send_verification_email(to_email, code):
    headers = {
        'Authorization': f'Bearer {RESEND_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'from': FROM_EMAIL,
        'to': to_email,
        'subject': 'Your TodoPro Verification Code',
        'html':f'''
    <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <div style="max-width: 500px; margin: auto; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 30px;">
            <div style="text-align: center;">
                <h2 style="color: #333;">Welcome to <span style="color: #0c66ff;">TodoPro</span> 🎉</h2>
            </div>
            <p style="font-size: 16px; color: #555;">Thanks for signing up! Please verify your email with the following code:</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; background-color: #0c66ff; color: white; font-size: 24px; padding: 12px 24px; border-radius: 6px;">
                    {code}
                </span>
            </div>
            <p style="font-size: 14px; color: #999; text-align: center;">If you didn’t create this account, you can safely ignore this email.</p>
        </div>
    </div>     
        '''
    }

    response = requests.post('https://api.resend.com/emails' , headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to send email: {response.text}")