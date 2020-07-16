from flask import Flask
from flask_manage_webpack import FlaskManageWebpack
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=''
    )
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    CORS(app)
    CORS(app, send_wildcard=True)

    manage_webpack = FlaskManageWebpack()
    manage_webpack.init_app(app)

    with app.app_context():
        import indice_pollution.api
        import indice_pollution.web

    return app
        