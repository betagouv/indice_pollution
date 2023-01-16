from celery import Celery
from flask_caching import Cache
import logging

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    db = None
else:
    db = SQLAlchemy()

celery = Celery(__name__)
cache = Cache()
logger = logging.getLogger(__name__)