from dateutil.parser import parse
from datetime import timedelta
from . import ForecastMixin

class Forecast(ForecastMixin):
    url = 'https://opendata.atmo-na.org/api/v1/indice/atmo/'
    zone_type = 'insee'

    @classmethod
    def insee_list(cls):
        return ['33063', '79005', '16102', '64102', '64445', '19272', '87085',
            '24322', '40088', '17300', '16015', '79191', '87154', '86194', '19031',
            '64300', '23096'
        ]

    @classmethod
    def params(cls, date, insee):
        tomorrow = (parse(date) + timedelta(hours=24)).date()

        return {
            'format': 'json',
            'zone': insee,
            'date_fin': str(tomorrow),
            'date_deb': date
        }

    @classmethod
    def getter(cls, feature):
        return {
            'indice': feature['properties']['valeur'],
            'date': str(parse(feature['properties']['date_ech']).date())
        }