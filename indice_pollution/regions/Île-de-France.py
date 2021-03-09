from . import ForecastMixin, EpisodeMixin
import os
import requests
from flask import current_app
from bs4 import BeautifulSoup
from datetime import date, timedelta

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
    get_only_from_scraping = True

    def get_from_scraping(self, to_return, date_, insee):
        api_key = os.getenv('AIRPARIF_API_KEY')
        polluant_code_pol = {
            "O3": "7",
            "NO2": "8",
            "PM10": "5"
        }
        if not api_key:
            return []
        r = requests.get(
            "https://api.airparif.asso.fr/episodes/en-cours-et-prevus",
            headers={
                "X-Api-Key": api_key,
                "accept": "application/json"
            })
        for k, date_ in [('jour', date.today()), ('demain', date.today() + timedelta(days=1))]:
            for polluant in r.json()[k]['polluants']:
                to_return += [{
                    'code_pol': polluant_code_pol.get(polluant['nom']),
                    'date': str(date_),
                    'etat': "PAS DE DEPASSEMENT" if polluant['niveau'] == "-" else polluant['niveau'],
                    'code_zone': insee[:2]
                }]
        return to_return

