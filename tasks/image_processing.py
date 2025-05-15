from celery_app import celery
from models.image_task import ImageTask
from bson import ObjectId
import time

@celery.task()
def process_image_task(task_id_str):
    from models.image_task import db  # reimport for child process
    task_id = ObjectId(task_id_str)

    task = db.image_tasks.find_one({"_id": task_id})
    if not task:
        return

    # Mock processing
    time.sleep(2)  # simulate processing delay
    processed_image = task["image_data"] + "_processed"  # mock effect

    ImageTask.update_status(task_id, "completed", result={"image": processed_image})
