import bcrypt
from bson.objectid import ObjectId

class User:
    """User model for MongoDB"""
    
    @staticmethod
    def create_user(mongo, email, name, password=None):
        """Create a new user"""
        user = {
            "email": email,
            "name": name,
            "role": "user"  # Set default role to "user"
        }
        
        # Hash password if provided
        if password:
            user["password"] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        result = mongo.db.users.insert_one(user)
        user['_id'] = result.inserted_id
        return user
    
    @staticmethod
    def find_by_email(mongo, email):
        """Find a user by email"""
        return mongo.db.users.find_one({"email": email})
    
    @staticmethod
    def find_by_id(mongo, user_id):
        """Find a user by ID"""
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    @staticmethod
    def compare_password(plain_password, hashed_password):
        """Compare a plain password with a hashed password"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
