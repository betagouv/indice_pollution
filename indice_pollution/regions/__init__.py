import requests

class ForecastMixin(object):
    url = ""
    epci_list = []
    insee_epci = dict()

    def get(self, date, insee=None):
        r = requests.get(
            self.url,
            params=self.params(date=date, insee=insee)
        )

        r.raise_for_status()

        return list(filter(lambda s: s is not None, map(self.getter, self.features(r))))

    def features(self, r):
        return r.json()['features']

    def params(self, date, insee):
        pass

    def getter(self, feature):
        pass

    def insee_list(self):
        return []