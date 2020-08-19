from . import ForecastMixin
from datetime import timedelta, datetime
import xml.etree.ElementTree as ET

class Forecast(ForecastMixin):
    website = 'https://www.atmosud.org/'
    url = 'https://geoservices.atmosud.org/geoserver/ind_sudpaca/ows?service=WFS&version=1.1.0'
    fr_date_format = '%d-%m-%Y 00:00:00'

    @classmethod
    def params(cls, date_, insee):
        parsed_date = datetime.strptime(date_, '%Y-%m-%d')
        tomorrow_date = parsed_date + timedelta(days=1)

        fr_date = parsed_date.strftime(cls.fr_date_format)
        fr_tomorrow = tomorrow_date.strftime(cls.fr_date_format)

        return {
            'service': 'WFS',
            'version': '1.1.0',
            'request': 'GetFeature',
            'typeName': 'ind_sudpaca:ind_sudpaca_agglo',
            'CQL_FILTER': f"code_zone='{insee}' AND (date_ech='{fr_date}' OR date_ech='{fr_tomorrow}')"
        }

    @classmethod
    def features(cls, r):
        root = ET.fromstring(r.text)
        return list(filter(lambda el: el.tag == '{http://ind_sudpaca}ind_sudpaca_agglo', root[0]))


    @classmethod
    def getter(cls, feature):
        feature_dict = {f.tag: f.text for f in feature}

        return {
            **{
            'indice': feature_dict['{http://ind_sudpaca}valeur'],
            'date': datetime.strptime(
                    feature_dict['{http://ind_sudpaca}date_ech'], cls.fr_date_format
                ).strftime('%Y-%m-%d')
            },
            **{
                k: feature_dict[f'{{http://ind_sudpaca}}{k}']
                for k in cls.outfields
                if f'{{http://ind_sudpaca}}{k}' in feature_dict
            }
        }

    @classmethod
    def insee_list(cls):
        return ['06029', '06088', '13001', '13055', '83137', '84007']