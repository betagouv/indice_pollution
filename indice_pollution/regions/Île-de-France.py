from . import ForecastMixin, EpisodeMixin
import requests
from flask import current_app
from bs4 import BeautifulSoup

class Service(object):
    website = 'https://www.airparif.asso.fr/'
    insee_list = ['75056']
    
    def get_close_insee(self, insee):
        return insee

class Forecast(Service, ForecastMixin):
    url = 'https://magellan.airparif.asso.fr/geoserver/DIDON/wfs'
    attributes_key = 'properties'
    use_dateutil_parser = True

    def params(self, date_, insee):
        return {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': f'DIDON:indice_atmo_2020',
            'outputFormat': 'application/json',
            'CQL_FILTER': f"date_ech >= '{date_}T00:00:00Z' AND code_zone={insee}"
        }

    def get_from_scraping(self, previous_results, date_, insee):
        r = requests.get('https://www.airparif.asso.fr/')
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        data =  soup.find_all('div', class_='indices_data')[0].find_all('div')
        indice = int(data[1].text)
        qualif = self.INDICE_TO_QUALIF[indice]

        return previous_results + [
            {"date": str(date_), "valeur": indice, "indice": indice, "qualif": qualif}
        ]

class Episode(Service, EpisodeMixin):
    url = 'https://services8.arcgis.com/gtmasQsdfwbDAQSQ/arcgis/rest/services/alrt_idf/FeatureServer/0/query'

    def params(self, insee, date_):
        return {
            'where': "date_ech >= CURRENT_DATE - INTERVAL '7' DAY",
            'outFields': '*',
            'outSR': '4326',
            'f': 'json'
        }
