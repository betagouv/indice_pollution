from indice_pollution.regions.solvers import insee_list
import requests
import logging
import time
import pytz
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import exc
from indice_pollution.history.models import IndiceHistory
from indice_pollution.models import db

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
        try:
            r = s.get(url, params=params)
        except requests.exceptions.ConnectionError as e:
            logging.error(f'Impossible de se connecter à {url}')
            logging.error(e)
            return None
        except requests.exceptions.SSLError as e:
            logging.error(f'Erreur ssl {url}')
            logging.error(e)
            return None
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.error(f'Erreur HTTP: {e}')
            return None
        return r

    def get_multiple_attempts(self, url, params, attempts=0):
        r = self.get_one_attempt(url, params)
        if r:
            features = self.features(r)
        else:
            features = []
        if attempts >= 3 or len(features) > 0:
            return features
        else:
            time.sleep(0.5 * (attempts + 1))
            return self.get_multiple_attempts(url, params, attempts+1)

    def get(self, date_, insee, attempts=0, force_from_db=False):
        to_return = []
        insee = self.get_close_insee(insee)
        if force_from_db:
            indice = IndiceHistory.get(date_, insee)
            if indice:
                return [indice.features]
        if not to_return:
            to_return = self.get_no_cache(date_, insee, attempts)
        if not to_return:
            to_return = IndiceHistory.get_after(date_, insee)
        if not any(map(lambda r: r['date'] == str(date_), to_return)):
            if hasattr(self, "get_from_scraping"):
                to_return = self.get_from_scraping(to_return, date_, insee)
        if to_return:
            for v in to_return:
                if not v.get('indice'):
                    continue
                indice = IndiceHistory.get_or_create(v['date'], insee)
                indice.features = v
                db.session.commit()
        return to_return

    def get_no_cache(self, date_, insee, attempts=0):
        features = self.get_multiple_attempts(self.url, self.params(date_, insee), attempts)
        return list(filter(lambda s: s is not None, map(self.getter, features)))

    def features(self, r):
        return r.json()['features']

    def where(self, date_, insee):
        zone = insee if not self.insee_epci else self.insee_epci[insee]
        return f"(date_ech >= '{date_}') AND (code_zone='{zone}')"

    def params(self, date_, insee):
        return {
            'where': self.where(date_, insee),
            'outFields': ",".join(self.outfields),
            'f': 'json',
            'outSR': '4326'
        }

    def getter(self, feature):
        pass

    @property
    def insee_list(self):
        return [] if not self.insee_epci else self.insee_epci.keys()

    def get_close_insee(self, insee):
        if insee in self.insee_list:
            return insee
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

    