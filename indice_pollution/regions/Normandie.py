from . import ForecastMixin
from dateutil.parser import parse
from json.decoder import JSONDecodeError
import orjson as json
from itertools import takewhile
from string import printable

class Forecast(ForecastMixin):
    url = 'https://dservices7.arcgis.com/FPRT1cIkPKcq73uN/arcgis/services/ind_normandie_agglo/WFSServer?service=wfs&request=getcapabilities'

    def params(self, date, insee):
        self.date = date
        self.insee = insee
        return {
            'service': 'wfs',
            'request': 'getfeature',
            'typeName': f'ind_normandie_agglo:ind_normandie_agglo',
            'outputFormat': 'geojson',
        }

    @classmethod
    def features(cls, r):
        try:
            return r.json()['features']
        except JSONDecodeError:
            set_printable = set(printable + 'éèàçôêùà')
            clean_string = str("".join(takewhile(lambda c: c in set_printable, r.text)))
            return json.loads(clean_string)['features']

    def getter(self, feature):
        str_date = str(parse(feature['properties']['date_ech']).date())
        if str_date < self.date:
            return None
        if str(feature['properties']['code_zone']) != self.insee:
            return None
        return {
            'indice': feature['properties']['valeur'],
            'date': str_date
        }

    @classmethod
    def insee_list(cls):
        return ['76351', '14366', '76540', '14118', '50502', '27229', '50129', '61001']
