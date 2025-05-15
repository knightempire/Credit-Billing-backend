from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()
image_tasks_collection = db.get_collection("image_tasks")

class ImageTask:
    @staticmethod
    def create_task(email, image_data, status="pending"):
        task = {
            "email": email,
            "image_data": image_data,
            "status": status,
            "created_at": datetime.utcnow(),
        }
        result = image_tasks_collection.insert_one(task)
        task["_id"] = str(result.inserted_id)
        return task

    @staticmethod
    def update_status(task_id, status, result=None):
        from bson import ObjectId
        update_fields = {"status": status}
        if result:
            update_fields["result"] = result
        image_tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_fields}
        )

    @staticmethod
    def find_task(task_id):
        from bson import ObjectId
        task = image_tasks_collection.find_one({"_id": ObjectId(task_id)})
        if task:
            task["_id"] = str(task["_id"])
        return task
