from celery import Celery


celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["workers.tasks"]
)

celery_app.conf.beat_schedule = {
    "delete-expired-tasks-every-5-minutes": {
        "task": "workers.tasks.delete_expired_tasks",
        "schedule": 60.0,
    }
}

celery_app.conf.timezone = "UTC"


