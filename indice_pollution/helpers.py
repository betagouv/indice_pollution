from datetime import datetime
import pytz
from flask import current_app
import requests


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

def ping(uuid):
    try:
        requests.get(f"https://hc-ping.com/{uuid}", timeout=10)
    except requests.RequestException as e:
        current_app.logger.error(f"Ping to healthchecks.io failed: {e}")
