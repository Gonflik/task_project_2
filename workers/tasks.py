import asyncio
from celery_app import celery_app
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from decouple import config
from models.task import Task, TaskStatus
from mails import send_deadline_miss_email

SYNC_DATABASE_URL = config('DATABASE_URL').replace('+asyncpg', '')

engine = create_engine(SYNC_DATABASE_URL)
print(f"Worker DB URL: {SYNC_DATABASE_URL}")
SessionLocal = sessionmaker(bind=engine)


@celery_app.task
def delete_expired_tasks():
    with SessionLocal() as session:
        stmt = select(Task).where(
            Task.due_date < datetime.now(timezone.utc),
            Task.status != TaskStatus.COMPLETED
        )
        expired_tasks = session.scalars(stmt).all()
        if not expired_tasks:
            return
        
        expired_ids = [task.id for task in expired_tasks]

        for task in expired_tasks:
            asyncio.run(send_deadline_miss_email(task.email, task.title))
        
        delete_stmt = delete(Task).where(Task.id.in_(expired_ids))
        result = session.execute(delete_stmt)

        session.commit()
        print(f"Deleted {result.rowcount} expired tasks")