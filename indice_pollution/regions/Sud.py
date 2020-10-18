from . import ForecastMixin
from datetime import timedelta, datetime

class Forecast(ForecastMixin):
    website = 'https://www.atmosud.org/'
    url = 'https://geoservices.atmosud.org/geoserver/ind_sudpaca/ows?service=WFS&version=1.1.0'
    fr_date_format = '%Y-%m-%dT00:00:00Z'

    insee_list = ['06029', '06088', '13001', '13055', '83137', '84007']

    attributes_key = 'properties'
    use_dateutil_parser = True

    @classmethod
    def params(cls, date_, insee):
        tomorrow_date = date_ + timedelta(days=1)

        fr_date = date_.strftime(cls.fr_date_format)
        fr_tomorrow = tomorrow_date.strftime(cls.fr_date_format)

        return {
            'service': 'WFS',
            'version': '1.1.0',
            'request': 'GetFeature',
            'typeName': 'ind_sudpaca:ind_sudpaca_agglo',
            'CQL_FILTER': f"code_zone='{insee}' AND (date_ech='{fr_date}' OR date_ech='{fr_tomorrow}')",
            'outputFormat': 'json'
        }
    def date_getter(self, attributes):
        return datetime.strptime(attributes['date_ech'], self.fr_date_format)
