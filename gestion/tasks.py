from __future__ import absolute_import, unicode_literals
from gestem.celery import app
from django.core.mail import EmailMessage
from django.conf import settings
import imaplib
import time


@app.task
def solicitud_email(subject, plain_message, from_email, to, html_message):

    email = EmailMessage(
        subject,
        html_message,
        from_email,
        to,
        # reply_to=['terstem12@gmail.com'],
    )
    email.content_subtype = 'html'
    email.send()

    # Con este código guardamos una copia en la carpeta imap enviados

    copia = str(email.message())
    imap = imaplib.IMAP4(settings.EMAIL_HOST_IMAP)
    imap.starttls()
    imap.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    imap.append(
        'INBOX.Sent',
        '\\SEEN',
        imaplib.Time2Internaldate(time.time()),
        copia.encode())
    imap.logout()
