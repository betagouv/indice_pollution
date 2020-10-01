from datetime import timedelta
from . import ForecastMixin
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Forecast(ForecastMixin):
    website = 'https://www.atmo-nouvelleaquitaine.org/'
    url = 'https://opendata.atmo-na.org/geoserver/ind_nouvelle_aquitaine_agglo/wfs'

    attributes_key = 'properties'
    use_dateutil_parser = True

    insee_list = [
        '33063', '79005', '16102', '64102', '64445', '19272', '87085', '24322', '40088',
        '17300', '16015', '79191', '87154', '86194', '19031', '64300', '23096'
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

    def get_no_cache(self, date_, insee, attempts=0):
        r = requests.get(f'https://www.atmo-nouvelleaquitaine.org/monair/commune/{insee}')
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