import uuid
from datetime import datetime


def keygen():
    fecha = datetime.now()
    año = fecha.strftime("%y")
    key = str(uuid.uuid4())
    return 'CTS963-' + año + (key[-6:]).upper()
