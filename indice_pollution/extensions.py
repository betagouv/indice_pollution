from celery import Celery
from flask_caching import Cache

try:
    from sqlalchemy import 
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    db = None
else:
    db = SQLAlchemy()

celery = Celery(__name__)
cache = Cache()
