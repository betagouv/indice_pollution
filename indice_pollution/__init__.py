from flask import Flask
from flask_manage_webpack import FlaskManageWebpack
from flask_cors import CORS
from .regions.solvers import region
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
    )
    CORS(app, send_wildcard=True)

    manage_webpack = FlaskManageWebpack()
    manage_webpack.init_app(app)

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
