import asyncio
from fastapi_mail import MessageSchema, MessageType, MultipartSubtypeEnum, NameEmail
from backend.app.core.celery_app import celery_app
from backend.app.core.logging import get_logger
from backend.app.core.emails.config import fastmail

logger = get_logger()

@celery_app.task(
    name="send_email_task",
    bind=True,
    max_retries=3,
    soft_time_limit=60,
    auto_retry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
)
def send_email_task(
    self, *, recipients: list[NameEmail], subject: str, html_content: str, plain_content: str
) -> bool:
    """Asynchronous task to send an email using FastAPI-Mail."""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_content,
            subtype=MessageType.html,
            alternative_body=plain_content,
            multipart_subtype=MultipartSubtypeEnum.alternative,
        )

        async def send_email():
            await fastmail.send_message(message, template_name=None)

        asyncio.run(send_email())
        logger.info(f"Email sent to {recipients} with subject '{subject}'")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
        return False