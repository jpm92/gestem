from gestem.settings.base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY_2')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ADMINS = [('Jesús Peña', "jesuspm92@gmail.com")]

CELERY_BROKER_URL = 'amqp://wmaster:134256@localhost/vhost'

STATIC_ROOT = "/srv/www/gestem/static/"

# SESSION_COOKIE_SECURE = True # Activar cuando este el SSL

# CSRF_COOKIE_SECURE = True

EMAIL_USE_TLS = True

SERVER_EMAIL = 'noreply_gestem@ugr.es' # This is the e-mail from which errors are sent.
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_IMAP = os.getenv('EMAIL_HOST_IMAP')
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
