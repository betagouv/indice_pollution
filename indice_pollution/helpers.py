from datetime import datetime
import pytz

def today():
    zone = pytz.timezone('Europe/Paris')
    return datetime.now(tz=zone).date()