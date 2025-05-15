# routes/users.py
from flask import Blueprint, request, jsonify, current_app
from controllers.users import login_controller, verify_token_controller,register_user,create_user_and_password
from middleware.auth.tokenvalidate import readverify_register_tokens, readverify_forgot_token, verify_register_token, verify_forgot_token , token_validator

users_bp = Blueprint('users', __name__)

@users_bp.route('/login', methods=['POST'])
def login():
    return login_controller(request)



@users_bp.route('/register', methods=['POST'])
def register():
    return register_user(request)

@users_bp.route('/create_user', methods=['POST'])
@verify_register_token
def create_user():
    return create_user_and_password(request)


@users_bp.route('/verify-register-token', methods=['GET'])
@readverify_register_tokens
def verify_register_token_route():
    # Your logic here (or just return success if decorator passes)
        return jsonify({
        "message": "Token verified successfully",
        "user": {
            "email": g.token_data["email"],
            "name": g.token_data["name"],
        },
    }), 200


@users_bp.route('/verify-forgot-token', methods=['GET'])
@readverify_forgot_token
def verify_forgot_route():
        return jsonify({
        "message": "Token verified successfully",
        "user": {
            "email": g.token_data["email"],
            "name": g.token_data["name"],
        },
    }), 200


@users_bp.route('/verify-token', methods=['GET'])
@token_validator
def verify_token():
    return jsonify({
        "message": "Token verified successfully",
        "user": {
            "email": g.token_data["email"],
            "name": g.token_data["name"],
            "role": g.token_data["role"]
        },
        "token": g.token_data["token"]
    }), 200
