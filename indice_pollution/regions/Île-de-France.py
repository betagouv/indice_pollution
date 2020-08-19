from . import ForecastMixin
from datetime import datetime, timedelta
from dateutil.parser import parse
import requests
import pytz
from flask import current_app

class Forecast(ForecastMixin):
    website = 'https://www.airparif.asso.fr/'
    url = 'https://services8.arcgis.com/gtmasQsdfwbDAQSQ/arcgis/rest/services/ind_idf_agglo/FeatureServer/0/query'

    @classmethod
    def insee_list(cls):
        return ['75056']

    @classmethod
    def params(cls, date_, insee):
        return {
            'where': f"date_ech >= CURRENT_DATE - INTERVAL '2' DAY",
            'outFields': "*",
            'f': 'json',
            'outSR': '4326'
        }

    @classmethod
    def getter(cls, feature):
        attributes = feature['attributes']
        zone = pytz.timezone('Europe/Paris')
        
        dt = str(datetime.fromtimestamp(attributes['date_ech']/1000, tz=zone).date())
        return {
            **{
                'indice': feature['attributes']['valeur'],
                'date': dt
            },
            **{k: feature['attributes'][k] for k in cls.outfields if k in feature['attributes']}
        }
    
    def get_close_insee(self, insee):
        return insee