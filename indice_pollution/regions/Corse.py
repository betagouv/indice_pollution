from . import ForecastMixin
from datetime import datetime

class Forecast(ForecastMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/ind_atmo_corse/FeatureServer/0/query'

    @classmethod
    def insee_list(cls):
        return ['2B096', '2B033', '2A004']

    @classmethod
    def params(cls, date, insee):
        return {
            'where': f"(date_ech >= '{date}') AND (code_zone='{insee}')",
            'outFields': 'valeur, date_ech',
            'f': 'json',
            'outSR': '4326'
        }

    @classmethod
    def getter(cls, feature):
        dt = datetime.utcfromtimestamp(feature['attributes']['date_ech']/1000)
        return {
            'indice': feature['attributes']['valeur'],
            'date': str(dt.date())
        }