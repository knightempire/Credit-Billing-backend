import jwt
import os
from flask import jsonify, current_app
from models.user import User
from datetime import datetime, timedelta
import bcrypt
from middleware.mail.mail import send_register_email, send_forgot_email
from middleware.auth.tokencreation import create_token

# Get the mongo instance from the app
def get_mongo():
    return current_app.extensions['pymongo'].cx.get_database()

def login_controller(request):
    """Handle user login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.find_by_email(email)
    print(f'User found: {user}')  # Debugging info

    if not user or 'password' not in user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Debug prints
    print("Entered password:", password)
    print("Stored hash:", user['password'])
    print("Password match:", User.compare_password(password, user['password']))

    if not User.compare_password(password, user['password']):
        return jsonify({"message": "Invalid password"}), 401

    # Generate JWT token
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "id": str(user['_id']),
        "name": user['name'],
        "email": user['email'],
        "role": user.get('role', 'user'),
        "exp": expiration
    }

    token = create_token(payload)

    return jsonify({
        "token": token,
        "user": {"name": user['name'], "email": user['email']}
    })

def verify_token_controller(request):
    """Verify JWT token"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    
    try:
        payload = jwt.decode(
            token, 
            os.environ.get("JWT_SECRET"),
            algorithms=["HS256"]
        )
        
        return jsonify({
            "user": {"username": payload['email'], "name": payload['name']}
        })
    
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401


def register_user(request):
    try:
        # Get data from the request body
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        user_type = "user"  # The type is hardcoded as 'user'
        
        print(f'email received: {email}')
        
        # Check if both email and name are provided
        if not email or not name:
            print('Missing email or name')
            return jsonify({'message': 'email and name are required'}), 400
        
        # Check if email already exists in the database
        print('Checking if email already exists')
        existing_user = User.find_by_email(email)
        print(f'Existing user: {existing_user}')
        if existing_user:
            print(f'email already exists: {email}')
            return jsonify({'message': 'email already exists'}), 400
        
        # Send registration email
        print(f'Creating new user instance with email: {email}')
        send_register_email(email, name, user_type)
        
        return jsonify({
            'status': 200,
            'message': 'email printed to console and email sent',
            'email': email
        }), 200
        
    except Exception as error:
        print(f'Error: {error}')
        return jsonify({'message': 'Internal server error'}), 500

    
def create_user_and_password(request):
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        print(f"Received email: {email}, name: {name}", f"password: {password}")

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        # No need to get mongo here since User uses module-level collection
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({'message': 'Email already exists'}), 400

        # Hash password manually OR just pass to create_user (which hashes)
        # But to keep your code consistent, hash here and pass hashed
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User.create_user(email=email, name=name, password=hashed_password)

        return jsonify({
            'status': 200,
            'message': 'User created successfully',
            'user': {
                'email': new_user['email'],
                'name': new_user['name'],
            }
        }), 201

    except Exception as error:
        print(f'Error in create_user_and_password: {error}')
        return jsonify({'message': 'Server error'}), 500


def forgot_password(request):
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')

        # Check if the email exists in the system
        user = User.find_by_email(get_mongo(), email)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Send the forgot password email
        send_forgot_email(email, name)
        
        return jsonify({
            'status': 200,
            'message': 'Password reset email sent successfully',
        }), 200

    except Exception as error:
        print(f'Error in forgot_password: {error}')
        return jsonify({'message': 'Server error'}), 500
