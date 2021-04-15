from . import ForecastMixin, EpisodeMixin
import requests
import json
from bs4 import BeautifulSoup
from dateutil.parser import parse
from .occitanie_epcis import insee_epci

class Service(object):
    is_active = True
    website = 'https://www.atmo-occitanie.org/'
    nom_aasqa = 'ATMO Occitanie'
    attributes_key = 'attributes'

class Episode(Service, EpisodeMixin):
    url = 'https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/epipol_3j_occitanie/FeatureServer/0/query'

class Forecast(Service, ForecastMixin):
    url = 'https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Indice_quotidien_de_qualit%C3%A9_de_l%E2%80%99air_pour_les_collectivit%C3%A9s_territoriales_en_Occitanie/FeatureServer/0/query'

    def params(self, date_, insee):
        zone = insee if not insee_epci else insee_epci[insee]
        return {
            'where': f"(date_ech >= CURRENT_DATE - INTERVAL '2' DAY) AND code_zone ='{zone}'",
            'outFields': "*",
            'f': 'json',
            'outSR': '4326'
        }

    IQA_TO_QUALIF = {
        "1": "tres_bon",
        "2": "bon",
        "3": "bon",
        "4": "bon",
        "5": "moyen",
        "6": "mediocre",
        "7": "mediocre",
        "8": "mediocre",
        "9": "mauvais",
        "10": "tres_mauvais"
    }

    def get_from_scraping(self, previous_results, date_, insee):
        r = requests.get(self.get_url(insee))
        soup = BeautifulSoup(r.text, 'html.parser')
        script = soup.find_all('script', {"data-drupal-selector": "drupal-settings-json"})[0]
        j = json.loads(script.contents[0])
        city_iqa = j['atmo_mesures']['city_iqa']
        occitanie_indice_dict = {
            '1': 'bon',
            '2': 'moyen',
            '3': 'degrade',
            '4': 'mauvais',
            '5': 'tres_mauvais',
            '6': 'extrement_mauvais'
        }
        return [
            self.getter({
                "indice": occitanie_indice_dict.get(v['iqa']),
                "date": str(parse(v['date']).date())
            })
            for v in city_iqa
        ]

    def get_url(self, insee):
        r = requests.get(f'https://geo.api.gouv.fr/communes/{insee}',
                params={
                    "fields": "codesPostaux",
                    "format": "json",
                    "geometry": "centre"
                }
        )
        codes_postaux = ",".join(r.json()['codesPostaux'])
        search_string = f"{r.json()['nom']} [{codes_postaux}]"
        r = requests.post(
            'https://www.atmo-occitanie.org/',
            data={
                "search_custom": search_string,
                "form_id": "city_search_block_form"
            },
            allow_redirects=False
        )
        return r.headers['Location']
