# routes/users.py
from flask import Blueprint, request, jsonify, current_app
from controllers.users import login_controller, verify_token_controller,register_user,create_user_and_password

users_bp = Blueprint('users', __name__)

@users_bp.route('/login', methods=['POST'])
def login():
    return login_controller(request)

@users_bp.route('/verify-token', methods=['GET'])
def verify_token():
    return verify_token_controller(request)


@users_bp.route('/register', methods=['POST'])
def register():
    return register_user()

@users_bp.route('/create_user', methods=['POST'])
def create_user():
    return create_user_and_password()