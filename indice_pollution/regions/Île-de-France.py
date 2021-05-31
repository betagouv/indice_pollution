from indice_pollution.history.models.zone import Zone
from . import ForecastMixin, EpisodeMixin
import os
import requests
import itertools
from flask import current_app
from datetime import date, timedelta

class Service(object):
    is_active = True
    website = 'https://www.airparif.asso.fr/'
    nom_aasqa = 'Airparif'
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

    @property
    def params_fetch_all(self):
        return {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': f'DIDON:indice_atmo_2020',
            'outputFormat': 'application/json',
            'CQL_FILTER': f'(date_dif >= {date.today()}) OR (date_ech = {date.today()})'
        }

    def get_from_scraping(self, previous_results, date_, insee):
        api_key = os.getenv('AIRPARIF_API_KEY')
        if not api_key:
            return []
        r = requests.get(
            f"https://api.airparif.asso.fr/indices/prevision/commune?insee={insee}",
            headers={
                "X-Api-Key": api_key,
                "accept": "application/json"
            })
        to_return = []
        for _k, indices in r.json().items():
            to_return = [
                self.getter({
                    "date": indice["date"],
                    "lib_qual": indice["indice"],
                })
                for indice in indices
                if "date" in indice and "indice" in indice
            ]
        return to_return



class Episode(Service, EpisodeMixin):
    url_fetch_all = 'https://opendata.arcgis.com/datasets/f4e0877c9e05459b8edf94077f1d2dbc_0.geojson'
    get_only_from_scraping = True

    params_fetch_all = {}

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
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            current_app.logger.error(e)
            return []
        try:
            r.json()
        except ValueError as e:
            current_app.logger.error(e)
            return []
        for k, date_ in [('jour', date.today()), ('demain', date.today() + timedelta(days=1))]:
            for polluant in r.json()[k]['polluants']:
                to_return += [{
                    'code_pol': polluant_code_pol.get(polluant['nom']),
                    'date': str(date_),
                    'etat': "PAS DE DEPASSEMENT" if polluant['niveau'] == "-" else polluant['niveau'],
                    'code_zone': insee[:2]
                }]
        return to_return

    @classmethod
    def get_zone_id(cls, properties):
        return Zone.query.filter_by(code='11', type='region').first().id