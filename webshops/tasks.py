from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives

from simpleAPI.celery_init import app

logger = get_task_logger(__name__)


@app.task(name="webshops.send_email", bind=True)
def send_email(
    self, subject, text_content, recipients, html_content=None,
    attachments=None, reply_to=None
):
    logger.info("sending email '%s'..." % subject)
    if reply_to is None:
        reply_to = settings.NO_REPLY_EMAIL

    _recipients = filter(None, recipients)
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.NO_REPLY_EMAIL,
        _recipients,
        reply_to=[reply_to]
    )
    if html_content:
        logger.info("attaching HTML alternative")
        msg.attach_alternative(html_content, "text/html")
    if attachments:
        for a in attachments:
            logger.info("attaching file: " + a.filename)
            msg.attach(a.filename, a.file, a.mime)
    if _recipients:
        msg.send()
        logger.info("sent successfully")
