from celery import Celery
import logging

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    db = None
else:
    db = SQLAlchemy()

celery = Celery(__name__)
logger = logging.getLogger(__name__)