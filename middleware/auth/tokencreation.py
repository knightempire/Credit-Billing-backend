import os
import jwt
import logging
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib
from dotenv import load_dotenv
from models.token import create_token_document, update_token_in_db

load_dotenv()

# Constants from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SECRET_KEY = os.getenv("MAIL_SECRET_KEY")
FORGOT_SECRET_KEY = os.getenv("FORGOT_SECRET_KEY")
EXPIRES_IN = int(os.getenv("EXPIRES_IN", 3600))  # Default expiration of 1 hour
MAIL_EXPIRES_IN = int(os.getenv("MAIL_EXPIRES_IN", 3600))  # Default expiration of 1 hour

def create_token(data):
    """Create a general JWT token for the given data."""
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY is not defined in the environment variables.')
    
    logging.info("Creating general token")

    try:
        # Set expiration time for the token
        expiration_time = datetime.utcnow() + timedelta(seconds=EXPIRES_IN)
        data['exp'] = expiration_time
        
        # Generate the token using HS256 algorithm (symmetric)
        token = jwt.encode(data, SECRET_KEY, algorithm='HS256')

        logging.info(f"Generated token for {data['email']}")

        return token

    except Exception as e:
        logging.error(f"Error during general token creation: {e}")
        raise


def register_mail_token(data):
    """Create a registration token for user and store it in MongoDB."""
    if not MAIL_SECRET_KEY:
        raise ValueError('MAIL_SECRET_KEY is not defined in the environment variables.')

    logging.info("Creating registration token")

    # Set expiration time for the registration token
    expiration_time = datetime.utcnow() + timedelta(seconds=MAIL_EXPIRES_IN)
    data['exp'] = expiration_time

    data['secret_key'] = MAIL_SECRET_KEY
    try:
        # Generate the token using the secret key (no need to hash it)
        token = jwt.encode(data, MAIL_SECRET_KEY, algorithm='HS256')

        # Create a token document and store it in MongoDB
        logging.info(f"Creating token document for {data['email']}")
        token_id = create_token_document(token, data['email'])
        update_token_in_db(token_id, token)

        logging.info(f"Generated and stored registration token for {data['email']} with ID: {token_id}")

        return token

    except Exception as e:
        logging.error(f"Error during registration token creation: {e}")
        raise  # Re-raise the exception so it can be handled properly



def forgot_mail_token(data):
    """Create a password reset token for user and store it in MongoDB."""
    if not FORGOT_SECRET_KEY:
        raise ValueError('FORGOT_SECRET_KEY is not defined in the environment variables.')

    logging.info("Creating forgot password token")

    try:
        # Set expiration time for the password reset token
        expiration_time = datetime.utcnow() + timedelta(seconds=MAIL_EXPIRES_IN)
        data['exp'] = expiration_time
        data['secret_key'] = FORGOT_SECRET_KEY
        # Generate the token using the HS256 algorithm (symmetric)
        token = jwt.encode(data, FORGOT_SECRET_KEY, algorithm='HS256')

        # Create a token document and store it in MongoDB
        token_id = create_token_document(token, data['email'])
        update_token_in_db(token_id, token)

        logging.info(f"Generated and stored forgot password token for {data['email']} with ID: {token_id}")

        return token
    
    except Exception as e:
        logging.error(f"Error during forgot password token creation: {e}")
        raise
