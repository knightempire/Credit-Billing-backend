# routes/users.py
from flask import Blueprint, request, jsonify, current_app
from controllers.users import login_controller, verify_token_controller,register_user,create_user_and_password
from middleware.auth.tokenvalidate import readverify_register_tokens, readverify_forgot_token, verify_register_token, verify_forgot_token , token_validator
from controllers.profile import (
    create_profile,
    view_profile,
    update_profile,
    delete_profile
)
from models.image_task import ImageTask
from tasks.image_processing import process_image_task
from flask import g


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


@users_bp.route('/profile/create', methods=['POST'])
@token_validator
def handle_create_profile():
    return create_profile(request)

@users_bp.route('/profile/<string:email>', methods=['GET'])
@token_validator
def handle_view_profile(email):
    return view_profile(request, email)

@users_bp.route('/profile/<string:email>', methods=['PUT'])
@token_validator
def handle_update_profile(email):
    return update_profile(request, email)

@users_bp.route('/profile/<string:email>', methods=['DELETE'])
@token_validator
def handle_delete_profile(email):
    return delete_profile(request, email)


@users_bp.route("/image-task", methods=["POST"])
@token_validator
def submit_image_task():
    data = request.get_json()
    email = g.token_data["email"]
    image_data = data.get("image_data")

    if not image_data:
        return jsonify({"error": "Missing image data"}), 400

    task = ImageTask.create_task(email, image_data)
    process_image_task.delay(task["_id"])  # Send to Celery

    return jsonify({"message": "Image processing started", "task": task}), 202