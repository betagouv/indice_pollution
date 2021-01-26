from indice_pollution.regions import ForecastMixin, EpisodeMixin
from dateutil.parser import parse
from datetime import timedelta, date, datetime

class Service(object):
    website = 'http://www.airpl.org/'
    use_dateutil_parser = True

    def get_close_insee(self, insee):
        return insee

class Episode(Service, EpisodeMixin):
    url = 'https://data.airpl.org/geoserver/alrt3j_pays_de_la_loire/wfs'
    attributes_key = 'properties'

    def params(self, date_, insee):
        departement = self.departement(insee)
        return {
            "version": "2.0.0",
            "typeName": "alrt3j_pays_de_la_loire:alrt3j_pays_de_la_loire",
            "service": "WFS",
            "outputFormat": "application/json",
            "request": "GetFeature",
            "CQL_FILTER": f"date_ech >= {date_}T00:00:00Z AND code_zone='{departement}'"
        }

class Forecast(Service, ForecastMixin):
    url = 'https://data.airpl.org/api/v1/indice/commune/'

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
