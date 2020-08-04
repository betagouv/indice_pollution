from . import ForecastMixin
from datetime import datetime

class Forecast(ForecastMixin):
    url = 'https://services3.arcgis.com/Is0UwT37raQYl9Jj/arcgis/rest/services/ind_Grand_Est_commune_3j/FeatureServer/0/query'
    @classmethod
    def insee_list(cls):
        return ['8105', '57463', '67180', '67482', '88160', '57672', '10387', '68224',
            '68297', '57227', '68066', '52448', '51454', '54395', '51108']

    @classmethod
    def params(cls, date, insee):
        return {
            'f': 'json',
            'outFields': 'code_zone,date_ech,valeur',
            'outSR': '4326',
            'where': f"(code_zone={insee}) AND (date_ech >= DATE '{date}')"
        }

    @classmethod
    def getter(cls, feature):
        dt = datetime.utcfromtimestamp(feature['attributes']['date_ech']/1000)
        return {
            'indice': feature['attributes']['valeur'],
            'date': str(dt.date())
        }
