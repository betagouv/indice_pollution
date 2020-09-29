from flask import Flask
from flask_manage_webpack import FlaskManageWebpack
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import pytz
import os

def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=''
    )
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('POSTGRESQL_ADDON_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    CORS(app, send_wildcard=True)

    manage_webpack = FlaskManageWebpack()
    manage_webpack.init_app(app)

    from .models import db
    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        import indice_pollution.api
        import indice_pollution.web
        import indice_pollution.history

    return app

def forecast(insee, date_=None, force_from_db=False):
    from .regions.solvers import region
    date_ = date_ or today()
    r = region(insee)
    return {
        "data": r.get(date_=date_, insee=insee, force_from_db=force_from_db),
        "metadata": {
            "region": {
                "nom": r.__module__.split(".")[-1],
                "website": r.website
            }
        }
    }

def today():
    zone = pytz.timezone('Europe/Paris')
    return datetime.now(tz=zone).date()