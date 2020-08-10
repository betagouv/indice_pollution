from . import ForecastMixin
from dateutil.parser import parse
from json.decoder import JSONDecodeError
import orjson as json
from itertools import takewhile
from string import printable

class Forecast(ForecastMixin):
    url = 'https://dservices7.arcgis.com/FPRT1cIkPKcq73uN/arcgis/services/ind_normandie_agglo/WFSServer?service=wfs&request=getcapabilities'

    @classmethod
    def params(cls, date, insee):
        filter_zone = f'<PropertyIsEqualTo><PropertyName>code_zone</PropertyName><Literal>{insee}</Literal></PropertyIsEqualTo>'
        filter_date = f'<PropertyIsGreaterThanOrEqualTo><PropertyName>date_ech</PropertyName><Literal>{date}T00:00:00.000Z</Literal></PropertyIsGreaterThanOrEqualTo>'
        return {
            'service': 'wfs',
            'request': 'getfeature',
            'typeName': f'ind_normandie_agglo:ind_normandie_agglo',
            'Filter': f"<Filter><And>{filter_zone}{filter_date}</And></Filter>",
            'outputFormat': 'geojson',
        }

    @classmethod
    def features(cls, r):
        r.encoding = 'utf8'
        try:
            return r.json()['features']
        except JSONDecodeError:
            set_printable = set(printable + 'éèàçôêùà')
            clean_string = str("".join(takewhile(lambda c: c in set_printable, r.text)))
            return json.loads(clean_string)['features']

    @classmethod
    def getter(cls, feature):
        str_date = str(parse(feature['properties']['date_ech']).date())
        return {
            **{
                'indice': feature['properties']['valeur'],
                'date': str_date
            },
            **{k: feature['properties'][k] for k in cls.outfields if k in feature}
        }

    @classmethod
    def insee_list(cls):
        return ['76351', '14366', '76540', '14118', '50502', '27229', '50129', '61001']
