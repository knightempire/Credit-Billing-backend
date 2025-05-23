import bcrypt
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import MongoClient
import os
import base64

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
users_collection = db.get_collection('users')

class User:
    """User model for MongoDB"""
    
    @staticmethod
    def create_user(email, name, password=None):
        """Create a new user document in MongoDB"""
        user = {
            "email": email,
            "name": name,
            "role": "user",  # Default role set to 'user'
            "createdAt": datetime.utcnow()  # Add creation time
        }
        
        # Hash password if provided
        if password:
            
            generated_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user["password"] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        result = users_collection.insert_one(user)
        user['_id'] = result.inserted_id
        return user
    
    @staticmethod
    def find_by_email(email):
        """Find a user by email from the database"""
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID from the database"""
        return users_collection.find_one({"_id": ObjectId(user_id)})
    
    @staticmethod
    def compare_password(plain_password, hashed_password):
        try:
            print("Entered password (raw):", plain_password)
            print("Stored bcrypt hash:", hashed_password)

            hashed_password = hashed_password.encode('utf-8')

            plain_password_bytes = plain_password.encode('utf-8')
            match = bcrypt.checkpw(plain_password_bytes, hashed_password)

            print("Password match result:", match)
            return match
        except Exception as e:
            print("Error comparing passwords:", e)
            return False

    @staticmethod
    def update_user(user_id, updated_data):
        """Update user data (e.g., name, role, etc.)"""
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updated_data}
        )
        return result.modified_count  # Return number of documents modified
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user from the database"""
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count  # Return the number of documents deleted
