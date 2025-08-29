# backend/celery_worker.py


from celery import Celery
from celery.result import AsyncResult
from backend import celery_config
from backend.ml_model import generate_image
# Import our ML function

# Create a Celery instance
celery_app = Celery('tasks')
# NEW CODE
celery_app.config_from_object('backend.celery_config')

# This is the background task that will be executed by a Celery worker
@celery_app.task
def generate_image_task(prompt: str):
    """
    A Celery task to generate an image.
    This runs in a separate process from the web server.
    """
    # This function is from Step 1!
    image_path = generate_image(prompt)
    # The return value will be stored in the result backend (Redis)
    return image_path

# Function to check the status of a task
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return result