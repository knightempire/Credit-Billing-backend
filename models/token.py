import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
tokens_collection = db.get_collection('tokens')

# Constants from environment variables
EXPIRES_IN = int(os.getenv("EXPIRES_IN", 3600))  # Default expiration of 1 hour
MAIL_EXPIRES_IN = int(os.getenv("MAIL_EXPIRES_IN", 3600))  # Default expiration of 1 hour

# Set TTL index for the collection (5 minutes default, or customizable)
tokens_collection.create_index([("createdAt", 1)], expireAfterSeconds=300)

def create_token_document(token, email):
    """Create a token document in MongoDB with expiration time."""
    new_token = {
        'token': token,
        'email': email,
        'createdAt': datetime.utcnow()  # Add creation time
    }
    result = tokens_collection.insert_one(new_token)
    return str(result.inserted_id)  # Return the inserted document's ID


def update_token_in_db(token_id, token):
    """Update the stored token in the database."""
    tokens_collection.update_one({'_id': token_id}, {'$set': {'token': token}})


def get_token_by_email(email):
    """Retrieve token by email from the database."""
    return tokens_collection.find_one({"email": email})
