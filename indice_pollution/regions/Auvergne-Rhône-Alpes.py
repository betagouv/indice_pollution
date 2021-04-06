from . import ForecastMixin, EpisodeMixin
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import current_app

class Service(object):
    is_active = True
    website = 'https://www.atmo-auvergnerhonealpes.fr/'
    nom_aasqa = 'Atmo Auvergne-Rhône-Alpes'

class Forecast(Service, ForecastMixin):
    get_only_from_scraping = True

    def get_from_scraping(self, previous_results, date_, insee):
        api_key = os.getenv('AURA_API_KEY')
        if not api_key:
            return []

        r = requests.get(f'https://api.atmo-aura.fr/api/v1/communes/{insee}/indices/atmo?api_token={api_key}&date_debut_echeance={date_}')
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            current_app.logger.error(e)
            return []
        indice_qual = {
            "Bon": "bon",
            "Moyen": "moyen",
            "Dégradé": "degrade",
            "Mauvais": "mauvais",
            "Très mauvais": "tres_mauvais",
            "Extrêmement mauvais": "extremement_mauvais"
        }

        return [
            self.getter({
                "date": indice['date_echeance'],
                "lib_qual": indice['qualificatif']
            })
            for indice in r.json()['data']
        ]


class Episode(Service, EpisodeMixin):
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/Episodes%20de%20pollution%20pr%C3%A9vus%20ou%20constat%C3%A9s/FeatureServer/0/query'

    def filtre_post_get(self, code_zone, date_):
        return lambda f: f.get('date') == str(date_)