# app.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Import routes and middleware
from routes.users import users_bp
from middleware.google_auth import init_google_auth

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure MongoDB
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)

# Configure CORS
CORS(app, origins=os.environ.get("CLIENT_URL"), supports_credentials=True)

# Configure session for OAuth
app.secret_key = os.environ.get("SESSION_SECRET", "keyboard cat")

# Print OAuth configuration for debugging
print(f"Google OAuth Configuration:")
print(f"Client ID: {os.environ.get('GOOGLE_CLIENT_ID', 'Not set')[:5]}...")
print(f"Callback URL: {os.environ.get('GOOGLE_CALLBACK_URL', 'Not set')}")

# Initialize Google Auth
init_google_auth(app, mongo)

# Register blueprints
app.register_blueprint(users_bp, url_prefix='/users')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server listening on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
