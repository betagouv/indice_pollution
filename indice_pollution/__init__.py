from itertools import groupby
from sqlalchemy.orm import joinedload
from indice_pollution.history.models.commune import Commune
from indice_pollution.history.models.indice_atmo import IndiceATMO
from indice_pollution.history.models.episode_pollution import EpisodePollution
from indice_pollution.history.models.indice_uv import IndiceUv
from flask import Flask
from flask_cors import CORS
from datetime import date, datetime
import os
from indice_pollution.history.models.raep import RAEP
from indice_pollution.history.models.vigilance_meteo import VigilanceMeteo

from .helpers import today, ping
from .extensions import celery, cache, db, migrate
from importlib import import_module
from kombu import Queue
from celery.schedules import crontab
from functools import partial

def configure_celery(flask_app):
    """Configure tasks.celery:
    * read configuration from flask_app.config and update celery config
    * create a task context so tasks can access flask.current_app
    Doing so is recommended by flask documentation:
    https://flask.palletsprojects.com/en/1.1.x/patterns/celery/
    """
    # Settings list:
    # https://docs.celeryproject.org/en/stable/userguide/configuration.html
    celery_conf = {
        key[len('CELERY_'):].lower(): value
        for key, value in flask_app.config.items()
        if key.startswith('CELERY_')
    }
    celery.conf.update(celery_conf)
    celery.conf.task_queues = (
        Queue("default", routing_key='task.#'),
        Queue("save_indices", routing_key='save_indices.#'),
    )
    celery.conf.task_default_exchange = 'tasks'
    celery.conf.task_default_exchange_type = 'topic'
    celery.conf.task_default_routing_key = 'task.default'

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

def configure_cache(app):
    conf = {
        "CACHE_TYPE": os.getenv("CACHE_TYPE", "SimpleCache"),
        "CACHE_DEFAULT_TIMEOUT": os.getenv("CACHE_DEFAULT_TIMEOUT", 86400),
    }
    if conf["CACHE_TYPE"] == "RedisCache":
        conf["CACHE_REDIS_HOST"] = os.getenv("REDIS_HOST")
        conf["CACHE_REDIS_PASSWORD"] = os.getenv("REDIS_PASSWORD")
        conf["CACHE_REDIS_PORT"] = os.getenv("REDIS_PORT")
        conf["CACHE_REDIS_TOKEN"] = os.getenv("REDIS_TOKEN")
        conf["CACHE_REDIS_URL"] = os.getenv("REDIS_URL")
    elif conf["CACHE_TYPE"] == "SimpleCache":
        conf["CACHE_THRESHOLD"] = 100000
    cache.init_app(app, conf)

@celery.task(bind=True)
def save_all_indices(self, module_name, class_name, launch_time=None):
    self.update_state(f"Saving {module_name}.{class_name}")
    module = import_module(module_name)
    if hasattr(module, "Service") and hasattr(module.Service, "is_active") and not module.Service.is_active:
        self.update_state(f"{module_name} is not active")
        return f"{module_name} is not active"
    if not hasattr(module, class_name):
        self.update_state(f"No class {class_name} in {module_name}")
        return f"No class {class_name} in {module_name}"
    cls_ = getattr(module, class_name)
    ping(cls_, "start", launch_time)
    try:
        cls_.save_all()
    except:
        ping(cls_, "fail")
    self.update_state(f"{module_name}.{class_name} saved")
    ping(cls_, "success", launch_time)
    return f"{module_name}.{class_name} saved"


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    add_periodic_task = partial(
        sender.add_periodic_task,
        schedule=crontab(minute='0', hour='*/1'),
        queue='save_indices',
        routing_key='save_indices.save_all'
    )

    regions = [
        'Auvergne-Rhône-Alpes',
        'Bourgogne-Franche-Comté',
        'Bretagne',
        'Centre-Val de Loire',
        'Corse',
        'Grand Est',
        'Guadeloupe',
        'Guyane',
        'Hauts-de-France',
        'Île-de-France',
        'Martinique',
        'Mayotte',
        'Normandie',
        'Nouvelle-Aquitaine',
        'Occitanie',
        'Pays de la Loire',
        "Réunion",
        "Sud"
    ]
    launch_time = datetime.now()
    for region in regions:
        add_periodic_task(sig=save_all_indices.s(f"indice_pollution.regions.{region}", "Forecast", launch_time))
        add_periodic_task(sig=save_all_indices.s(f"indice_pollution.regions.{region}", "Episode", launch_time))

    add_periodic_task(sig=save_all_indices.s("indice_pollution.history.models.raep", "RAEP", launch_time))
    add_periodic_task(sig=save_all_indices.s("indice_pollution.history.models.vigilance_meteo", "VigilanceMeteo", launch_time))

    add_periodic_task(sig=save_all_indices.s("indice_pollution.history.models.indice_uv", "IndiceUv", launch_time))


def init_app(app):
    db.init_app(app)
    configure_celery(app)
    configure_cache(app)

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
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND') or f"db+{app.config['SQLALCHEMY_DATABASE_URI']}"
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL') or f"sqla+{app.config['SQLALCHEMY_DATABASE_URI']}"

    CORS(app, send_wildcard=True)

    init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        import indice_pollution.api
        import indice_pollution.history

    return app

def make_resp(r, result, date_=None):
    if type(result) == list:
        if date_:
            result = [v for v in result if v['date'] == str(date_)]
    elif hasattr(result, 'dict'):
        result = [result.dict()]
    else:
        result = [result]
    return {
        "data": result,
        "metadata": make_metadata(r)
    }

def make_metadata(r):
    return {
        "region": {
            "nom": r.__name__.split(".")[-1],
            "website": r.Service.website,
            "nom_aasqa": r.Service.nom_aasqa
        }
    }

def forecast(insee, date_=None, use_make_resp=True):
    from .regions.solvers import get_region
    date_ = date_ or today()
    try:
        region = get_region(insee)
    except KeyError:
        return {
            "error": f"No region for {insee}",
            "metadata": {}
        }, 400
    if region.Service.is_active:
        indice = IndiceATMO.get(insee=insee, date_=date_)
        if use_make_resp:
            return make_resp(region, indice, date_)
        else:
            if indice is not None:
                indice.region = region
                indice.commune = Commune.get(insee)
            return indice
    else:
        indice = IndiceATMO()
        indice.region = region
        indice.commune = Commune.get(insee)
        indice.error = "Inactive region"
        return indice


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_all(date_):
    from indice_pollution.history.models import IndiceATMO, EpisodePollution
    date_ = date_ or today()
    indices = IndiceATMO.get_all(date_)
    episodes = EpisodePollution.get_all(date_)
    allergenes_par_departement = {
            r.zone_id: r
            for r in RAEP.get_all()
        }
    vigilances_par_departement = {
        zone_id: list(vigilances)
        for zone_id, vigilances in groupby(
            sorted(
                VigilanceMeteo.get_all(date_=date_),
                key=lambda v: v.zone_id
            ),
            lambda v: v.zone_id
        )
    }
    indices_uv = IndiceUv.get_all(date_)
    return (indices, episodes, allergenes_par_departement, vigilances_par_departement, indices_uv)


def episodes(insee, date_=None, use_make_resp=True):
    from .regions.solvers import get_region
    date_ = date_ or today()
    if type(date_) == str:
        date_ = date.fromisoformat(date_)

    region = get_region(insee)
    if region.Service.is_active:
        result = EpisodePollution.get(insee=insee, date_=date_)
        if use_make_resp:
            result = list(map(lambda e: e.dict(), result))
            return make_resp(region, result, date_)
        else:
            for r in result:
                r.region = region
                r.commune = Commune.get(insee)
            return result
    else:
        if use_make_resp:
            return {
                "error": "Inactive region",
                "metadata": make_metadata(region)
            }, 400
        else:
            episode = EpisodePollution()
            episode.region = region
            episode.commune = Commune.get(insee)
            episode.error = "Inactive region"
            return [episode]

def availability(insee):
    from .regions.solvers import get_region
    try:
        return get_region(insee).Service.is_active
    except KeyError:
        return False
    except AttributeError:
        return False


def raep(insee, date_=None, extended=False, departement_as_dict=True):
    if insee is None:
        return {}
    departement = Commune.get(insee).departement
    if not departement:
        return {}
    data = RAEP.get(zone_id=departement.zone_id, date_=date_)
    return {
        "departement": {
            "nom": departement.nom,
            "code": departement.code,
            "charniere": departement.charniere
        } if departement_as_dict else departement,
        "data": data.to_dict() if data else None
    }