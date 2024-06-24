"""Different application utils."""
import os
import smtplib
import ssl

from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost')

GMAIL_SMTP_PORT = 587
GMAIL_SMTP = 'smtp@gmail.com'


@app.task()
def send_email(receiver_email, message):
    """Sent email via gmail smtp."""
    sender_email = os.environ.get('smtp_sender')
    smtp_password = os.environ.get('smtp_password')
    with smtplib.SMTP_SSL(GMAIL_SMTP, GMAIL_SMTP_PORT) as smtp_client:
        smtp_client.ehlo()
        smtp_client.starttls(context=ssl.SSLContext(ssl.PROTOCOL_TLS))
        smtp_client.ehlo()
        smtp_client.login(sender_email, smtp_password)
        smtp_client.sendmail(sender_email, receiver_email, message)
