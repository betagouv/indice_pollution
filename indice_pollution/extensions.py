from celery import Celery
from flask_manage_webpack.manage_webpack import FlaskManageWebpack
from flask_migrate import Migrate
from flask_caching import Cache

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    db = None
else:
    db = SQLAlchemy()

celery = Celery(__name__)
cache = Cache()
manage_webpack = FlaskManageWebpack()
migrate = Migrate()