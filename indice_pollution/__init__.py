from flask import Flask
from flask_manage_webpack import FlaskManageWebpack
from flask_cors import CORS
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
alembic = Alembic()

from .regions.solvers import region
from datetime import date
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
        SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('POSTGRESQL_ADDON_URI')
    )
    CORS(app, send_wildcard=True)

    manage_webpack = FlaskManageWebpack()
    manage_webpack.init_app(app)

    db.init_app(app)
    alembic.init_app(app)

    with app.app_context():
        import indice_pollution.api
        import indice_pollution.web

    return app

def forecast(insee, date_=None):
    zone = pytz.timezone('Europe/Paris')
    date_ = date_ or date.now(tz=zone).date().isoformat()
    r = region(insee)
    return {
        "data": r.get(date_=date_, insee=insee),
        "metadata": {
            "region": {
                "nom": r.__module__.split(".")[-1],
                "website": r.website
            }
        }
    }
