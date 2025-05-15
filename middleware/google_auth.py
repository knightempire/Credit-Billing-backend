import os
import jwt
import requests
from urllib.parse import urlencode
from flask import redirect, url_for, session, request
from models import User

def init_google_auth(app, mongo):
    """Initialize Google OAuth authentication"""

    # Google OAuth configuration
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    callback_url = os.environ.get("GOOGLE_CALLBACK_URL")

    print(f"DEBUG - Using callback URL: {callback_url}")
    import jwt
    print(jwt.__file__)

    @app.route('/auth/google')
    def google_login():
        """Initiate Google OAuth flow"""
        # Build the Google OAuth URL manually
        auth_params = {
            'client_id': client_id,
            'redirect_uri': callback_url,
            'scope': 'email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }

        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(auth_params)}"
        print(f"DEBUG - Authorization URL: {auth_url}")

        return redirect(auth_url)

    @app.route('/auth/google/callback')
    def google_callback():
        """Handle Google OAuth callback"""
        # Get the authorization code from the request
        code = request.args.get('code')

        if not code:
            print("DEBUG - No code received in callback")
            return redirect(f"{os.environ.get('CLIENT_URL')}/login?error=auth_failed")

        # Exchange the code for an access token
        token_params = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': callback_url,
            'grant_type': 'authorization_code'
        }

        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_params)

        if not token_response.ok:
            print(f"DEBUG - Token exchange failed: {token_response.text}")
            return redirect(f"{os.environ.get('CLIENT_URL')}/login?error=auth_failed")

        token_data = token_response.json()
        access_token = token_data.get('access_token')

        # Get user info from Google
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if not user_info_response.ok:
            print(f"DEBUG - Failed to get user info: {user_info_response.text}")
            return redirect(f"{os.environ.get('CLIENT_URL')}/login?error=auth_failed")

        user_info = user_info_response.json()

        # Check if user exists by email
        user = User.find_by_email(mongo, user_info['email'])

        # If not, create a new user
        if not user:
            # Create new user
            user = User.create_user(
                mongo,
                email=user_info['email'],
                name=user_info['name']
            )

        # Generate JWT token
        token = jwt.encode(
            {"id": str(user['_id']), "name": user['name'], "email": user['email']},
            os.environ.get("JWT_SECRET"),
            algorithm="HS256",
            headers={"exp": 3600}  # 1 hour expiration
        )

        # Redirect to client with token
        client_url = os.environ.get("CLIENT_URL")
        return redirect(f"{client_url}/auth/login?token={token}")
