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

def make_resp(r, result):
    return {
        "data": result,
        "metadata": {
            "region": {
                "nom": r.__module__.split(".")[-1],
                "website": r.website
            }
        }
    }

def forecast(insee, date_=None, force_from_db=False):
    from .regions.solvers import region
    date_ = date_ or today()
    forecast = region(insee).Forecast()
    result = forecast.get(date_=date_, insee=insee, force_from_db=force_from_db)
    return make_resp(forecast, result)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def bulk(insee_region_names, date_=None, fetch_episodes=False):
    from indice_pollution.history.models import IndiceHistory, EpisodeHistory
    from .regions.solvers import region as get_region
    date_ = date_ or today()

    insees = set(insee_region_names.keys())
    close_insees = set()
    for insee in insees:
        region = get_region(region_name=insee_region_names[insee])
        close_insee = region.Forecast().get_close_insee(insee)
        close_insees.add(close_insee)
    insees.update(close_insees)

    indices = dict()
    episodes = dict()
    for chunk in chunks(list(insees), 10):
        indices.update(
            {i.insee: [i.features] for i in IndiceHistory.get_bulk(date_, chunk)}
        )
        if fetch_episodes:
            episodes.update(
                {i.code_zone: [i.features] for i in EpisodeHistory.get_bulk(date_, chunk)}
            )
    for insee in insee_region_names.keys():
        if insee in indices:
            continue
        region = get_region(region_name=insee_region_names[insee])
        f = region.Forecast()
        close_insee = f.get_close_insee(insee)
        if close_insee in indices:
            indices[insee] = indices[close_insee]
            continue
        indices[insee] = f.get(date_=date_, insee=insee, force_from_db=False)
    if fetch_episodes:
        for insee in insee_region_names.keys():
            if insee in episodes:
                continue
            region = get_region(region_name=insee_region_names[insee])
            e = region.Episode()
            close_insee = e.get_close_insee(insee)
            if close_insee in episodes:
                episodes[insee] = episodes[close_insee]
                continue
            episodes[insee] = e.get(date_=date_, insee=insee, force_from_db=False)
    to_return = {
        insee: {
            "forecast": make_resp(
                get_region(region_name=insee_region_names[insee]).Forecast(),
                indices[insee]
               ),
        }
        for insee in insee_region_names.keys()
    }
    if fetch_episodes:
        for insee in insee_region_names:
            to_return[insee].update({
                "episode": make_resp(
                    get_region(region_name=insee_region_names[insee]).Episode(),
                    episodes[insee]
                )
                }
            )
    return to_return

def today():
    zone = pytz.timezone('Europe/Paris')
    return datetime.now(tz=zone).date()

def episode(insee, date_=None):
    from .regions.solvers import region
    zone = pytz.timezone('Europe/Paris')
    date_ = date_ or today()
    episode = region(insee).Episode()
    return {
        "data": episode.get(date_=date_, insee=insee),
        "metadata": {
            "region": {
                "nom": episode.__module__.split(".")[-1],
                "website": episode.website
            }
        }
    }
