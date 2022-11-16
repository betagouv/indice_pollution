from datetime import datetime
import pytz
from flask import current_app
import requests
import os
from unidecode import unidecode

def today():
    zone = pytz.timezone('Europe/Paris')
    return datetime.now(tz=zone).date()

def oxford_comma(items):
    if not items:
        return
    items = list(items)
    length = len(items)
    if length == 0:
        return
    elif length == 1:
        return items[0]
    elif length == 2:
        return '{} et {}'.format(*items)
    else:
        return '{}, et {}'.format(', '.join(items[:-1]), items[-1])

def get_healthchecksio_slug(caller):
    cls_types = [
        {"start": "<class 'indice_pollution.regions.", "end": ".Forecast'>", "debut_slug": "import-indice_atmo-"},
        {"start": "<class 'indice_pollution.regions.", "end": ".Episode'>", "debut_slug": "import-episode_pollution-"},
        {"start": "<class 'indice_pollution.history.models.raep", "end": ".RAEP'>", "debut_slug": "import-raep"},
        {"start": "<class 'indice_pollution.history.models.vigilance_meteo", "end": ".VigilanceMeteo'>", "debut_slug": "import-vigilance_meteo"},
        {"start": "<class 'indice_pollution.history.models.indice_uv", "end": ".IndiceUv'>", "debut_slug": "import-indice_uv"},
    ]
    str_cls = str(caller)
    for cls_type in cls_types:
        if str_cls.startswith(cls_type["start"]) and str_cls.endswith(cls_type["end"]):
            raw_name = str_cls[len(cls_type["start"]):-(len(cls_type["end"]))]
            return cls_type["debut_slug"] + unidecode(raw_name.lower().replace(" ", "-"))


def ping(caller, ping_type):
    if not (slug := get_healthchecksio_slug(caller)):
        return
    ping_key = os.getenv("HEALTCHECKSIO_API_KEY")
    end_url = f"/{ping_type}" if ping_type != "success" else ""
    try:
        requests.get(f"https://hc-ping.com/{ping_key}/{slug}{end_url}", timeout=10)
    except requests.RequestException as e:
        current_app.logger.error(f"Ping to healthchecks.io failed: {e}")
