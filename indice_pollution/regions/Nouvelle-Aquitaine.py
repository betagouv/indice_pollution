from datetime import timedelta
from . import ForecastMixin, EpisodeMixin
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ..history.models import Commune
import logging

class Service(object):
    website = 'https://www.atmo-nouvelleaquitaine.org/'
    attributes_key = 'properties'
    use_dateutil_parser = True

    insee_list = [
        '33063', '79005', '16102', '64102', '64445', '19272', '87085', '24322', '40088',
        '17300', '16015', '79191', '87154', '86194', '19031', '64300', '23096'
    ]

    def get_close_insee(self, insee):
        return insee

class Episode(Service, EpisodeMixin):
    url = 'https://opendata.atmo-na.org/geoserver/alrt3j_nouvelle_aquitaine/wfs'

    def params(self, date_, insee):
        commune = Commune.get(insee)
        filter_zone = f'<PropertyIsEqualTo><PropertyName>code_zone</PropertyName><Literal>{commune.code_departement}</Literal></PropertyIsEqualTo>'
        filter_date = f'<PropertyIsGreaterThanOrEqualTo><PropertyName>date_dif</PropertyName><Literal>{date_}T00:00:00.000Z</Literal></PropertyIsGreaterThanOrEqualTo>'

        return {
            'request': 'GetFeature',
            'version': '1.0.0',
            'typeName': 'alrt3j_nouvelle_aquitaine:alrt3j_nouvelle_aquitaine',
            'where': '',
            'outfields': self.outfields,
            'outputFormat': 'json',
            'outSR': '4326',
            'Filter': f"<Filter><And>{filter_zone}{filter_date}</And></Filter>",
        }

class Forecast(Service, ForecastMixin):
    url = 'https://opendata.atmo-na.org/geoserver/ind_nouvelle_aquitaine_agglo/wfs'

    @classmethod
    def params(cls, date_, insee):
        filter_zone = f'<PropertyIsEqualTo><PropertyName>code_zone</PropertyName><Literal>{insee}</Literal></PropertyIsEqualTo>'
        filter_date = f'<PropertyIsGreaterThanOrEqualTo><PropertyName>date_ech</PropertyName><Literal>{date_}T00:00:00Z</Literal></PropertyIsGreaterThanOrEqualTo>'
        return {
            'service': 'wfs',
            'request': 'getfeature',
            'typeName': 'ind_nouvelle_aquitaine_agglo:ind_nouvelle_aquitaine_agglo',
            'Filter': f"<Filter><And>{filter_zone}{filter_date}</And></Filter>",
            'outputFormat': 'json',
        }

    def get_from_scraping(self, previous_results, date_, insee):
        url = f'https://www.atmo-nouvelleaquitaine.org/monair/commune/{insee}'
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            logging.error(f'Impossible de se connecter à {url}')
            logging.error(e)
            return []
        except requests.exceptions.SSLError as e:
            logging.error(f'Erreur ssl {url}')
            logging.error(e)
            return []
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        controls = soup.find_all('div', class_='day-controls')
        days = controls[0].find_all('a', class_='raster-control-link')

        return [
            self.getter({
                "date": str(datetime.fromtimestamp(int(day.attrs.get('data-rasterid'))).date()),
                "indice": int(int(day.attrs.get('data-index'))/10),
            })
            for day in days
        ]