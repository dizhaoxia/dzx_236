import jwt
import datetime
import hashlib
import secrets
from functools import wraps
from flask import request, jsonify, g
from config import Config

SECRET_KEY = Config.SECRET_KEY
JWT_EXPIRATION_HOURS = Config.JWT_EXPIRATION_HOURS

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hash_hex = stored.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False

def generate_jwt(user_id: int, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'code': 401, 'message': '未提供认证令牌'}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({'code': 401, 'message': '认证格式错误'}), 401
        token = parts[1]
        payload = decode_jwt(token)
        if not payload:
            return jsonify({'code': 401, 'message': '令牌无效或已过期'}), 401
        g.user_id = payload['user_id']
        g.email = payload['email']
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    return getattr(g, 'user_id', None)
