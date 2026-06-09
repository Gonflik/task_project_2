from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from decouple import config

mail_config = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME"),
    MAIL_PASSWORD=config("MAIL_PASSWORD"),
    MAIL_FROM=config("MAIL_USERNAME"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)


fastmail = FastMail(mail_config)

async def send_completion_email(email: str, task_title: str):
    message = MessageSchema(
        subject="Task COMPLETED!",
        recipients=[email],
        body=f"Your task '{task_title}' has been marked as completed!",
        subtype="plain"
    )
    await fastmail.send_message(message)

async def send_deadline_miss_email(email: str, task_title: str):
    message = MessageSchema(
        subject="Task deadline missed!",
        recipients=[email],
        body=f"Your task '{task_title}' deadline has passed and it's still not completed! Tsk tsk...",
        subtype="plain"
    )
    await fastmail.send_message(message)

