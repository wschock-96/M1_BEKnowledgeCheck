from jose import jwt
import jose
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app

SECRET_KEY = "your_secret_key"

def encode_auth_token(user_id, role='user'):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
        "role": role
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data['sub']
            request.user_id = user_id

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jose.exceptions.JWTError:
            return jsonify({"message": "Token is invalid!"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data['sub']
            role = data.get('role')
            request.user_id = user_id

            if role not in {"admin", "mechanic"}:
                return jsonify({"error": "Insufficient permissions!"}), 403

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        # except jose.exceptions.JWTError:
        #     return jsonify({"message": "Token is invalid!"}), 401
        except jose.exceptions.JWTError as e:
            print("JWT Decode Error:", e)
            return jsonify({"message": "Token is invalid!", "details": str(e)}), 401

        print("Decode SECRET_KEY:", current_app.config['SECRET_KEY'])
        
        return f(*args, **kwargs)
    
    return decorated