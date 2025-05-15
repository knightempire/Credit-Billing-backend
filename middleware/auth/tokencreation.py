import os
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from models.token import create_token_document, update_token_in_db
import logging


from dotenv import load_dotenv
load_dotenv()

# Constants from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SECRET_KEY = os.getenv("MAIL_SECRET_KEY")
FORGOT_SECRET_KEY = os.getenv("FORGOT_SECRET_KEY")
EXPIRES_IN = int(os.getenv("EXPIRES_IN", 3600)) 
MAIL_EXPIRES_IN = int(os.getenv("MAIL_EXPIRES_IN", 3600))  # Default expiration of 1 hour

private_key_path = os.path.join(os.path.dirname(__file__), '../rsa/private_key.pem')

def get_private_key():
    """Reads the private key from the PEM file."""
    try:
        with open(private_key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key
    except Exception as e:
        logging.warning(f"⚠️ Private key not found or unreadable at {private_key_path}. Using fallback value '123'.")
        return "123"

def create_token(data):
    """Create a JWT token for the given data."""
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY is not defined in the environment variables.')
    
    private_key = get_private_key()
    
    data['secret_key'] = SECRET_KEY
    expiration_time = datetime.utcnow() + timedelta(seconds=EXPIRES_IN)

    # Generate the token
    token = jwt.encode(data, private_key, algorithm='RS256', expires=expiration_time)
    return token


def register_mail_token(data):
    """Create a registration token for user and store it in MongoDB."""
    if not MAIL_SECRET_KEY:
        raise ValueError('MAIL_SECRET_KEY is not defined in the environment variables.')

    logging.info("register_mail_token")

    data['secret_key'] = MAIL_SECRET_KEY

    # Generate the token
    token = create_token(data)

    # Create a token document and store it in MongoDB
    token_id = create_token_document(token, data['email'])

    logging.info(f"Created and stored registration token for {data['email']} with ID: {token_id}")

    # Update the token in MongoDB with the generated token
    update_token_in_db(token_id, token)

    logging.info(f"Updated Token for {data['email']}: {token}")
    return token


def forgot_mail_token(data):
    """Create a password reset token for user and store it in MongoDB."""
    if not FORGOT_SECRET_KEY:
        raise ValueError('FORGOT_SECRET_KEY is not defined in the environment variables.')

    logging.info("forgot_mail_token")

    data['secret_key'] = FORGOT_SECRET_KEY

    # Generate the token
    token = create_token(data)

    # Create a token document and store it in MongoDB
    token_id = create_token_document(token, data['email'])

    logging.info(f"Created and stored forgot password token for {data['email']} with ID: {token_id}")

    # Update the token in MongoDB with the generated token
    update_token_in_db(token_id, token)

    logging.info(f"Updated Token for {data['email']}: {token}")
    return token
