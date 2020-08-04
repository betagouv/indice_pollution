import requests

class ForecastMixin(object):
    url = ""
    epci_list = []
    insee_epci = dict()

    @classmethod
    def get(cls, date, insee=None):
        r = requests.get(
            cls.url,
            params=cls.params(date=date, insee=insee)
        )

        r.raise_for_status()

        return list(filter(lambda s: s is not None, map(cls.getter, cls.features(r))))

    @classmethod
    def features(cls, r):
        return r.json()['features']

    @classmethod
    def params(cls, date, insee):
        pass

    @classmethod
    def getter(cls, feature):
        pass

    @classmethod
    def insee_list(cls):
        return []