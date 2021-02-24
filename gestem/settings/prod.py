from gestem.settings.base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY_2')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ADMINS = [('Jesús Peña', "jesuspm92@gmail.com")]

CELERY_BROKER_URL = 'amqp://wmaster:134256@localhost/vhost'

EMAIL_USE_TLS = True

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_IMAP = os.getenv('EMAIL_HOST_IMAP')
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
