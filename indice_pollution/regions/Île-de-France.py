from . import ForecastMixin
from datetime import datetime, timedelta
from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup
from flask import current_app

class Forecast(ForecastMixin):
    website = 'https://www.airparif.asso.fr/'
    url = 'https://services8.arcgis.com/gtmasQsdfwbDAQSQ/arcgis/rest/services/ind_idf_agglo/FeatureServer/0/query'

    insee_list = ['75056']

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
    
    def get_close_insee(self, insee):
        return insee

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