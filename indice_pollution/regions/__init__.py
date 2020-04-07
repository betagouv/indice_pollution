import requests

class ForecastMixin(object):
    url = ""
    epci_list = []
    insee_epci = dict()

    @classmethod
    def get(cls, date, epci=None, insee=None):
        print(f'date:{date} epci:{epci} insee:{insee}')
        r = requests.get(
            cls.url,
            params=cls.params(date=date, epci=epci, insee=insee)
        )

        r.raise_for_status()

        return list(map(cls.getter, r.json()['features']))

    @classmethod
    def params(cls, date, epci=None, insee=None):
        pass

    @classmethod
    def getter(cls, feature):
        pass

    @classmethod
    def insee_list(cls):
        return []