from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
profiles_collection = db.get_collection('profiles')


class Profile:
    """Profile model for MongoDB with images and payment subschemas"""

    @staticmethod
    def create_profile(email, credit=0, images=None, payment=None):
        profile = {
            "email": email,
            "credit": credit,
            "images": images if images else [],
            "payment": payment if payment else {},
            "createdAt": datetime.utcnow()
        }
        result = profiles_collection.insert_one(profile)
        profile["_id"] = result.inserted_id
        return profile

    @staticmethod
    def find_by_email(email):
        return profiles_collection.find_one({"email": email})

    @staticmethod
    def add_image(email, image_data):
        """Add a new image to the user's profile"""
        return profiles_collection.update_one(
            {"email": email},
            {"$push": {"images": image_data}}
        )

    @staticmethod
    def update_payment(email, payment_data):
        """Update payment information for the user"""
        return profiles_collection.update_one(
            {"email": email},
            {"$set": {"payment": payment_data}}
        )

    @staticmethod
    def update_credit(email, new_credit):
        """Update the credit value"""
        return profiles_collection.update_one(
            {"email": email},
            {"$set": {"credit": new_credit}}
        )

    @staticmethod
    def delete_profile(email):
        return profiles_collection.delete_one({"email": email})

    @staticmethod
    def update_profile(email, update_data):
        """Update profile fields (credit, images, payment)"""
        result = profiles_collection.update_one(
            {"email": email},
            {"$set": update_data}
        )

        if result.modified_count:
            return profiles_collection.find_one({"email": email})
        return None
