from . import ForecastMixin
from datetime import datetime

class Forecast(ForecastMixin):
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/ind_atmo_aura/FeatureServer/0/query'
    @classmethod
    def insee_list(cls):
        return ['73065', '74081', '43157', '69123', '73248', '03190', '74012', '38544',
            '73011', '63300', '01053', '74056', '03310', '03185', '42187', '15014', '38185',
            '74010', '42218', '26362', '38053', '01328', '63113'
        ]


    @classmethod
    def params(cls, date, insee=None):
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
