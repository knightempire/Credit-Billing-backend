import threading
import time
from models.image_task import ImageTask

def process_image_async(task_id):
    def _task():
        task = ImageTask.find_task(task_id)
        if not task:
            return

        # Simulate image processing delay
        time.sleep(20)
        processed_data = task['image_data'] + "_processed"

        ImageTask.update_status(task_id, "completed", result={"processed_data": processed_data})

    threading.Thread(target=_task).start()
