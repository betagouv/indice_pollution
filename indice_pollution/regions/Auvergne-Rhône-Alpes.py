from . import ForecastMixin
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Forecast(ForecastMixin):
    website = 'https://www.atmo-auvergnerhonealpes.fr/'
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/ind_atmo_aura/FeatureServer/0/query'
    
    insee_list = [
        '73065', '74081', '43157', '69123', '73248', '03190', '74012', '38544', '73011',
        '63300', '01053', '74056', '03310', '03185', '42187', '15014', '38185', '74010',
        '42218', '26362', '38053', '01328', '63113'
    ]

    COLOR_TO_QUALIF = {
        "0": "tres_bon",
        "21": "bon",
        "31": "bon",
        "41": "bon",
        "51": "moyen",
        "61": "mediocre",
        "71": "mediocre",
        "81": "mediocre",
        "91": "mauvais",
        "100": "tres_mauvais"
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

    def get_close_insee(self, insee):
        return insee