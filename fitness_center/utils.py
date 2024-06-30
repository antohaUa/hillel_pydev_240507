"""Different application utils."""
import os
import smtplib
import ssl

from celery import Celery
from email.message import EmailMessage

BROKER_TEMPLATE = 'pyamqp://{0}:{1}@{2}'
BROKER = BROKER_TEMPLATE.format(os.environ.get('RABBITMQ_DEFAULT_USER', 'guest'),
                                os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest'),
                                os.environ.get('RABBITMQ_HOST', 'localhost'))
app = Celery('tasks', broker=BROKER)

GMAIL_SMTP_PORT = 587
GMAIL_SMTP = 'smtp.gmail.com'


@app.task
def send_email(receiver_email, subject, text):
    """Sent email via gmail smtp."""
    sender_email = os.environ.get('smtp_sender')
    smtp_password = os.environ.get('smtp_password')

    # create email message with related fields
    emsg = EmailMessage()
    emsg.set_content(text)
    emsg['Subject'] = subject
    emsg['From'] = sender_email
    emsg['To'] = receiver_email

    # communicate with server and send meaage
    with smtplib.SMTP(GMAIL_SMTP, GMAIL_SMTP_PORT) as smtp_client:
        smtp_client.ehlo()
        smtp_client.starttls(context=ssl.SSLContext(ssl.PROTOCOL_TLS))
        smtp_client.ehlo()
        smtp_client.login(sender_email, smtp_password)
        smtp_client.send_message(emsg)
