try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    db = None
else:
    db = SQLAlchemy()

from celery import Celery
celery = Celery(__name__)