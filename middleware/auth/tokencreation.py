# middleware/auth/tokencreation.py

import os
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from models.token import create_token_document, update_token_in_db
import logging
import hashlib



from dotenv import load_dotenv
load_dotenv()

# Constants from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SECRET_KEY = os.getenv("MAIL_SECRET_KEY")
FORGOT_SECRET_KEY = os.getenv("FORGOT_SECRET_KEY")
EXPIRES_IN = int(os.getenv("EXPIRES_IN"))  # Default expiration of 1 hour
MAIL_EXPIRES_IN = int(os.getenv("MAIL_EXPIRES_IN"))  # Default expiration of 1 hour

def create_token(data):
    """Create a JWT token for the given data."""
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY is not defined in the environment variables.')

    logging.info("create_token")
    
    # Ensure SECRET_KEY is a valid RSA private key in PEM format
    try:
        private_key = SECRET_KEY  # The RSA private key in PEM format

        # Add private key to the data (if needed for further use)
        data['secret_key'] = private_key

        # Set expiration time for the token
        expiration_time = datetime.utcnow() + timedelta(seconds=EXPIRES_IN)
        data['exp'] = expiration_time

        # Generate the token using RS256 algorithm (ensure you're using an RSA private key)
        token = jwt.encode(data, private_key, algorithm='RS256')

        logging.info(f"Generated token for {data['email']}")

        return token
    
    except Exception as e:
        logging.error(f"Error during token creation: {e}")
        raise



def register_mail_token(data):
    """Create a registration token for user and store it in MongoDB."""
    print("register_mail_token")
    
    if not MAIL_SECRET_KEY:
        raise ValueError('MAIL_SECRET_KEY is not defined in the environment variables.')

    # Hash the MAIL_SECRET_KEY using SHA-256 (or any other hash algorithm)
    hashed_secret_key = hashlib.sha256(MAIL_SECRET_KEY.encode('utf-8')).hexdigest()
    print(f"Hashed MAIL_SECRET_KEY: {hashed_secret_key}")
    
    # Add the hashed key to the data for logging (or other purposes)
    data['MAIL_SECRET_KEY'] = hashed_secret_key
    print(f"data: {data}")

    # Set expiration time (ensure MAIL_EXPIRES_IN is defined)
    expiration_time = datetime.utcnow() + timedelta(seconds=MAIL_EXPIRES_IN)
    print(f"expiration_time: {expiration_time}")
    
    # Set the 'exp' claim for expiration
    data['exp'] = expiration_time
    
    try:
        # Generate the token using the hashed secret key
        token = jwt.encode(data, hashed_secret_key, algorithm='HS256')  # HS256 for a hashed key
        print(f"Generated token: {token}")

        # Create a token document and store it in MongoDB
        print(f"Creating token document for {data['email']}")
        token_id = create_token_document(token, data['email'])

        logging.info(f"Created and stored registration token for {data['email']} with ID: {token_id}")

        # Update the token in MongoDB with the generated token
        update_token_in_db(token_id, token)
        
        logging.info(f"Updated Token for {data['email']}: {token}")
        return token

    except Exception as e:
        print(f"Error during token creation: {e}")
        raise

def forgot_mail_token(data):
    """Create a password reset token for user and store it in MongoDB."""
    if not FORGOT_SECRET_KEY:
        raise ValueError('FORGOT_SECRET_KEY is not defined in the environment variables.')

    logging.info("forgot_mail_token")

    # Ensure FORGOT_SECRET_KEY is a valid RSA private key in PEM format
    try:
        # This is where we assume FORGOT_SECRET_KEY is a private key (PEM format).
        private_key = FORGOT_SECRET_KEY  # Ensure this key is a private RSA key in PEM format

        # Add private key to the data (if needed for further use)
        data['FORGOT_SECRET_KEY'] = private_key

        # Set expiration time for the token
        expiration_time = datetime.utcnow() + timedelta(seconds=MAIL_EXPIRES_IN)
        data['exp'] = expiration_time

        # Generate the token using RS256 algorithm (ensure you're using an RSA private key)
        token = jwt.encode(data, private_key, algorithm='RS256')

        # Create a token document and store it in MongoDB
        token_id = create_token_document(token, data['email'])

        logging.info(f"Created and stored forgot password token for {data['email']} with ID: {token_id}")

        # Update the token in MongoDB with the generated token
        update_token_in_db(token_id, token)

        logging.info(f"Updated Token for {data['email']}: {token}")
        return token
    
    except Exception as e:
        logging.error(f"Error during token creation: {e}")
        raise