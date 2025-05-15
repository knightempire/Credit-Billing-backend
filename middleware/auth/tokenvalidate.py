import os
import logging
from flask import Flask, request, jsonify
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from bson import ObjectId
from functools import wraps
from flask import request, jsonify, g  
from functools import wraps

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup for MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
token_collection = db.tokens

# Environment variables for secret keys
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SECRET_KEY = os.getenv("MAIL_SECRET_KEY")
FORGOT_SECRET_KEY = os.getenv("FORGOT_SECRET_KEY")

# JWT Token verification for general token

def token_validator(func):
    @wraps(func)  # ← THIS IS CRUCIAL
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.user = {
                "email": payload.get("email"),
                "name": payload.get("name"),
                "role": payload.get("role")
            }
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'MESSAGE': f'Invalid token: {str(e)}'}), 401

    return wrapper

# Token verification for admin token

def admintoken_validator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            if payload.get('role') != 'admin':
                return jsonify({'MESSAGE': 'You are not authorized to access this resource.'}), 401

            g.admin_user = {
                "email": payload.get("email"),
                "name": payload.get("name"),
                "role": payload.get("role"),
                "token": token
            }

            return func(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper

def readverify_register_tokens(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        if not token_header or not token_header.startswith('Bearer '):
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        token = token_header.split(' ')[1]

        try:
            existing_token = token_collection.find_one({"token": token})
            if not existing_token:
                return jsonify({'MESSAGE': 'Token not found or already used.'}), 401

            payload = jwt.decode(token, MAIL_SECRET_KEY, algorithms=["HS256"])
            print('Decoded JWT payload:', payload)

            if payload.get('secret_key') != MAIL_SECRET_KEY:
                return jsonify({'MESSAGE': 'Invalid token payload.'}), 401

            g.register_user = {
                'email': payload.get('email'),
                'name': payload.get('name'),
                'id': payload.get('id'),
                'token': token
            }

            return func(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'MESSAGE': f'Invalid token: {str(e)}'}), 401
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return jsonify({'MESSAGE': 'Unexpected server error.'}), 500

    return wrapper

# Token verification for "forgot" token
def readverify_forgot_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        if not token_header or not token_header.startswith('Bearer '):
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        token = token_header.split(' ')[1]

        try:
            existing_token = token_collection.find_one({"token": token})
            if not existing_token:
                return jsonify({'MESSAGE': 'Token not found or already used.'}), 401

            payload = jwt.decode(token, FORGOT_SECRET_KEY, algorithms=["HS256"])
            print('Decoded JWT payload:', payload)

            if payload.get('secret_key') != FORGOT_SECRET_KEY:
                return jsonify({'MESSAGE': 'Invalid token payload.'}), 401

            g.forgot_user = {
                'email': payload.get('email'),
                'name': payload.get('name'),
                'id': payload.get('id'),
                'token': token
            }

            return func(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'MESSAGE': f'Invalid token: {str(e)}'}), 401
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return jsonify({'MESSAGE': 'Unexpected server error.'}), 500

    return wrapper



# Token verification for "register" token with validation of token in the DB
def verify_register_token(func):
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            # Decode the token using the secret key
            payload = jwt.decode(token, MAIL_SECRET_KEY, algorithms=["HS256"])

            if payload.get('secret_key') == MAIL_SECRET_KEY:
                # Check if the token exists in the database
                existing_token = token_collection.find_one({"token": token})

                if not existing_token:
                    return jsonify({'MESSAGE': 'Token has already been used or expired.'}), 401

                # Attach user info to request
                request.json['email'] = payload.get('email')
                request.json['userId'] = payload.get('id')
                request.json['name'] = payload.get('name')

                # Remove the token from the DB after use
                token_collection.delete_one({"token": token})

                return func(*args, **kwargs)
            else:
                return jsonify({'MESSAGE': 'Invalid register token payload.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Register token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper

# Token verification for "forgot" token with validation of token in the DB
def verify_forgot_token(func):
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            # Decode the token using the secret key
            payload = jwt.decode(token, FORGOT_SECRET_KEY, algorithms=["HS256"])

            if payload.get('secret_key') == FORGOT_SECRET_KEY:
                # Check if the token exists in the database
                existing_token = token_collection.find_one({"token": token})

                if not existing_token:
                    return jsonify({'MESSAGE': 'Token has already been used or expired.'}), 401

                # Attach user info to request
                request.json['email'] = payload.get('email')
                request.json['userId'] = payload.get('id')
                request.json['name'] = payload.get('name')

                # Remove the token from the DB after use
                token_collection.delete_one({"token": token})

                return func(*args, **kwargs)
            else:
                return jsonify({'MESSAGE': 'Invalid forgot token payload.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Forgot token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper
