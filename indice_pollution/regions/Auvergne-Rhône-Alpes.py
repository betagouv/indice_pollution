from . import ForecastMixin, EpisodeMixin
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Service(object):
    website = 'https://www.atmo-auvergnerhonealpes.fr/'
    insee_list = [
        '73065', '74081', '43157', '69123', '73248', '03190', '74012', '38544', '73011',
        '63300', '01053', '74056', '03310', '03185', '42187', '15014', '38185', '74010',
        '42218', '26362', '38053', '01328', '63113'
    ]

    def get_close_insee(self, insee):
        return insee

class Forecast(Service, ForecastMixin):
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/ind_atmo_aura/FeatureServer/0/query'

    COLOR_TO_QUALIF = {
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
        r = requests.get(f'https://www.atmo-auvergnerhonealpes.fr/monair/commune/{insee}')
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        controls = soup.find_all('div', class_='day-controls')
        days = controls[0].find_all('a', class_='raster-control-link')

        return [
            {
                "date": str(datetime.fromtimestamp(int(day.attrs.get('data-rasterid'))).date()),
                "indice": int(int(day.attrs.get('data-index'))/10),
                "qualif": self.COLOR_TO_QUALIF[day.attrs.get('data-color')]
            }
            for day in days
        ]


class Episode(Service, EpisodeMixin):
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/Episodes%20de%20pollution%20pr%C3%A9vus%20ou%20constat%C3%A9s/FeatureServer/0/query'
