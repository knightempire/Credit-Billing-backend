import os
import logging
from flask import request, jsonify
from pymongo import MongoClient
import jwt
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Environment variables for secret keys
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SECRET_KEY = os.getenv("MAIL_SECRET_KEY")
FORGOT_SECRET_KEY = os.getenv("FORGOT_SECRET_KEY")

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
token_collection = db.tokens


# Token verification for general user tokens
def token_validator(func):
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            # Decode the token using the same secret key
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            # Check if the token's payload matches the expected structure
            request.json['email'] = payload.get('email')
            request.json['userId'] = payload.get('id')
            request.json['name'] = payload.get('name')
            request.json['rollNo'] = payload.get('rollNo')
            request.json['isFaculty'] = payload.get('isFaculty')

            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper

# Token verification for "admin" token
def admintoken_validator(func):
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:

   
            payload = jwt.decode(token, algorithms=["RS256"])

            if payload.get('secret_key') == SECRET_KEY:
                request.json['email'] = payload.get('email')
                request.json['userId'] = payload.get('id')
                request.json['name'] = payload.get('name')
                request.json['rollNo'] = payload.get('rollNo')
                request.json['isFaculty'] = payload.get('isFaculty')
                request.json['isAdmin'] = payload.get('isAdmin')

                if not payload.get('isAdmin'):
                    return jsonify({'MESSAGE': 'You are not authorized to access this resource.'}), 401

                return func(*args, **kwargs)
            else:
                return jsonify({'MESSAGE': 'Invalid token payload.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper

# Token verification for "register" token
def readverify_register_tokens(func):
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            existing_token = token_collection.find_one({"token": token})

            if not existing_token:
                return jsonify({'MESSAGE': 'Token not found in database or has already been used.'}), 401

            payload = jwt.decode(token, algorithms=["RS256"])

            if payload.get('MAIL_SECRET_KEY') == MAIL_SECRET_KEY:
                request.json['email'] = payload.get('email')
                request.json['userId'] = payload.get('id')
                request.json['name'] = payload.get('name')
                request.json['phoneNo'] = payload.get('phoneNo')
                request.json['isFaculty'] = payload.get('isFaculty')

                return func(*args, **kwargs)
            else:
                return jsonify({'MESSAGE': 'Invalid token payload.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper

# Token verification for "forgot" token
def readverify_forgot_token(func):
    def wrapper(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        token = token_header.split(' ')[1] if token_header else None

        if not token:
            return jsonify({'MESSAGE': 'Missing or invalid token.'}), 401

        try:
            existing_token = token_collection.find_one({"token": token})

            if not existing_token:
                return jsonify({'MESSAGE': 'Token not found in database or has already been used.'}), 401

       
      
            payload = jwt.decode(token, algorithms=["RS256"])

            if payload.get('FORGOT_SECRET_KEY') == FORGOT_SECRET_KEY:
                request.json['email'] = payload.get('email')
                request.json['userId'] = payload.get('id')
                request.json['name'] = payload.get('name')

                return func(*args, **kwargs)
            else:
                return jsonify({'MESSAGE': 'Invalid token payload.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'MESSAGE': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"JWT InvalidTokenError: {e}")
            return jsonify({'MESSAGE': f'Invalid or expired token: {str(e)}'}), 401

    return wrapper
