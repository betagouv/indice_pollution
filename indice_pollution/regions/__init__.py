import requests
from requests_cache.core import CachedSessions
import logging
import time

class ForecastMixin(object):
    url = ""
    epci_list = []
    insee_epci = dict()
    outfields = ['date_ech', 'valeur', 'qualif', 'val_no2', 'val_so2',
     'val_o3', 'val_pm10', 'val_pm25'
    ]

    def get(self, date, insee=None, attempts=0):
        if insee not in self.insee_list():
            insee = self.get_close_insee(insee)

        if attempts == 0:
            r = requests.get(
                self.url,
                params=self.params(date=date, insee=insee)
            )
        else:
            s = CachedSession()
            with s.cache_disabled():
                r = requests.get(
                    self.url,
                    params=self.params(date=date, insee=insee)
                )


        r.raise_for_status()

        to_return = list(filter(lambda s: s is not None, map(self.getter, self.features(r))))

        if attempts >= 3 or len(to_return) > 0:
            return to_return
        else:
            time.sleep(0.5 * (attempts + 1))
            return self.get(date, insee, attempts+1)

    def features(self, r):
        return r.json()['features']

    def params(self, date, insee):
        pass

    def getter(self, feature):
        pass

    def insee_list(self):
        return []

    def get_close_insee(self, insee):
        departement = insee[:2]
        try:
            return next(pref_insee for pref_insee in self.insee_list() if pref_insee[:2] == departement)
        except StopIteration:
            logging.error(f'Impossible de trouver le code insee de la préfecture de {insee}')
            raise KeyError
