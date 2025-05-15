import os
from flask import jsonify, current_app
from models.profile import Profile
from middleware.auth.tokencreation import create_token
from datetime import datetime

# Get the mongo instance from the app
def get_mongo():
    return current_app.extensions['pymongo'].cx.get_database()

# Create a new profile
def create_profile(request):
    """Handle creating a new user profile"""
    data = request.get_json()
    email = data.get('email')
    credit = data.get('credit', 0)
    images = data.get('images', [])
    payment = data.get('payment', {})

    # Check if required fields are present
    if not email :
        return jsonify({"message": "Email and name are required!"}), 400
    
    # Check if profile already exists
    existing_profile = Profile.find_by_email(email)
    if existing_profile:
        return jsonify({"message": "Profile with this email already exists!"}), 400

    # Create the profile
    profile = Profile.create_profile(email=email, credit=credit, images=images, payment=payment)

    if profile:
        return jsonify(profile), 201  # Created
    else:
        return jsonify({"message": "Failed to create profile"}), 500

# View a profile by email
def view_profile(request, email):
    """Fetch the profile details of the user by email"""
    profile = Profile.find_by_email(email)

    if not profile:
        return jsonify({"message": "Profile not found"}), 404

    return jsonify(profile), 200  # OK

# Update the profile (e.g., credit, images, payment)
def update_profile(request, email):
    """Update user profile details (e.g., credit, images, payment)"""
    data = request.get_json()
    credit = data.get('credit')
    images = data.get('images')
    payment = data.get('payment')

    profile = Profile.find_by_email(email)

    if not profile:
        return jsonify({"message": "Profile not found"}), 404

    # Update fields if provided
    update_data = {}
    if credit is not None:
        update_data['credit'] = credit
    if images is not None:
        update_data['images'] = images
    if payment is not None:
        update_data['payment'] = payment

    # Update profile in the database
    updated_profile = Profile.update_profile(email=email, update_data=update_data)

    if updated_profile:
        return jsonify(updated_profile), 200  # OK
    else:
        return jsonify({"message": "Failed to update profile"}), 500

# Delete the profile by email
def delete_profile(request, email):
    """Delete user profile by email"""
    profile = Profile.find_by_email(email)

    if not profile:
        return jsonify({"message": "Profile not found"}), 404

    # Delete the profile from the database
    result = Profile.delete_profile(email=email)

    if result.deleted_count == 1:
        return jsonify({"message": "Profile deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete profile"}), 500
