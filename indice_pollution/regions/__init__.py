import requests
import logging
import time
import pytz
from datetime import datetime
from dateutil.parser import parse

class ForecastMixin(object):
    url = ""
    epci_list = []
    insee_epci = dict()
    outfields = ['date_ech', 'valeur', 'qualif', 'val_no2', 'val_so2',
     'val_o3', 'val_pm10', 'val_pm25'
    ]

    attributes_key = 'attributes'
    use_dateutil_parser = False

    HTTPAdapter = requests.adapters.HTTPAdapter

    def get_one_attempt(self, url, params):
        s = requests.Session()
        s.mount('https://', self.HTTPAdapter())
        r = s.get(url, params=params)
        r.raise_for_status()
        return r

    def get_multiple_attempts(self, url, params, attempts=0):
        r = self.get_one_attempt(url, params)
        features = self.features(r)
        if attempts >= 3 or len(features) > 0:
            return features
        else:
            time.sleep(0.5 * (attempts + 1))
            return self.get_multiple_attempts(url, params, attempts+1)

    def get(self, date_, insee, attempts=0):
        if insee not in self.insee_list:
            insee = self.get_close_insee(insee)
        features = self.get_multiple_attempts(self.url, self.params(date_, insee))
        return list(filter(lambda s: s is not None, map(self.getter, features)))

    def features(self, r):
        return r.json()['features']

    def params(self, date_, insee):
        zone = insee if self.insee_list else self.insee_list[insee]
        return {
            'where': f"(date_ech >= '{date_}') AND (code_zone='{zone}')",
            'outFields': ",".join(self.outfields),
            'f': 'json',
            'outSR': '4326'
        }

    def getter(self, feature):
        pass

    @property
    def insee_list(self):
        return []

    def get_close_insee(self, insee):
        departement = insee[:2]
        try:
            return next(pref_insee for pref_insee in self.insee_list if pref_insee[:2] == departement)
        except StopIteration:
            logging.error(f'Impossible de trouver le code insee de la préfecture de {insee}')
            raise KeyError

    def getter(self, feature):
        attributes = feature[self.attributes_key]

        dt = self.date_getter(attributes)
        return {
            **{
                'indice': attributes['valeur'],
                'date': str(dt.date())
            },
            **{k: attributes[k] for k in self.outfields if k in attributes}
        }

    def date_getter(self, attributes):
        if not self.use_dateutil_parser:
            zone = pytz.timezone('Europe/Paris')
            return datetime.fromtimestamp(attributes['date_ech']/1000, tz=zone)
        else:
            return parse(attributes['date_ech'])

    