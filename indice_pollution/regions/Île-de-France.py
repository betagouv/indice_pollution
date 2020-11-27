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
    url = 'https://services8.arcgis.com/gtmasQsdfwbDAQSQ/arcgis/rest/services/ind_idf_agglo/FeatureServer/0/query'


    INDICE_TO_QUALIF = {
        0: "tres_bon",
        1: "tres_bon",
        2: "bon",
        3: "bon",
        4: "bon",
        5: "moyen",
        6: "mediocre",
        7: "mediocre",
        8: "mediocre",
        9: "mauvais",
        10: "tres_mauvais"
    }

    def where(self, date_, insee):
        return f"date_ech >= CURRENT_DATE - INTERVAL '2' DAY"

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
            'where': '1=1',
            'outFields': '*',
            'outSR': '4326',
            'f': 'json'
        }
