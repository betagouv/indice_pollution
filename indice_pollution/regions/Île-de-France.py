from . import ForecastMixin
from datetime import datetime, timedelta
from dateutil.parser import parse
import requests


class Forecast(ForecastMixin):
    date_format = '%Y-%m-%d'
    url = 'https://services8.arcgis.com/gtmasQsdfwbDAQSQ/arcgis/rest/services/ind_idf_agglo/FeatureServer/0/query'

    @classmethod
    def insee_list(cls):
        return ['75056', '95394']

    @classmethod
    def params(cls, date, insee):
        day_before = (
                datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)
            ).strftime('%Y-%m-%d')

        return {
            'where': f"date_ech >= DATE '{day_before}'",
            'outFields': 'valeur, date_ech, code_zone',
            'f': 'json',
            'outSR': '4326'
        }

    @classmethod
    def getter(cls, feature):
        attributes = feature['attributes']
        dt = datetime.fromtimestamp(attributes['date_ech']/1000).strftime(cls.date_format)
        return {
            'indice': feature['attributes']['valeur'],
            'date': dt
        }