from . import ForecastMixin, EpisodeMixin
from dateutil.parser import parse
from datetime import timedelta

class Service(object):
    website = 'http://www.airpl.org/'
    attributes_key = 'properties'
    use_dateutil_parser = True

    def get_close_insee(self, insee):
        return insee

class Episode(Service, EpisodeMixin):
    url = 'https://data.airpl.org/geoserver/alrt3j_pays_de_la_loire/wfs'

    def params(self, date_, insee):
        centre = self.centre(insee)

        return {
            'where': '',
            'outfields': self.outfields,
            'outputFormat': 'application/json',
            'geometry': f'{centre[0]},{centre[1]}',
            'inSR': '4326',
            'outSR': '4326',
            'geometryType': 'esriGeometryPoint',
            'request': 'GetFeature',
            'typeName': 'alrt3j_pays_de_la_loire'
        }

class Forecast(Service, ForecastMixin):
    url = 'https://data.airpl.org/api/v1/indice/commune/?commune=53001&export=json&date__range=2020-9-1,2021-1-4'

    @classmethod
    def params(cls, date_, insee):
        max_date = date_ + timedelta(days=1)
        return {
            "commune": insee,
            "date__range": f"{date_},{max_date}",
            "export": "json"
        }

    def features(self, r):
        return r.json().get('results', [])

    def attributes_getter(self, feature):
        return feature

    def getter(self, feature):
        return super().getter({
            "sous_indices": feature.get('sous_indice'),
            **feature
        })
