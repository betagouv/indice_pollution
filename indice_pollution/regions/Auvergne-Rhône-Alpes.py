from . import ForecastMixin, EpisodeMixin
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Service(object):
    website = 'https://www.atmo-auvergnerhonealpes.fr/'

class Forecast(Service, ForecastMixin):
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/Indice_ATMO/FeatureServer/0/query'
    use_dateutil_parser = True
    outfields = '*'

    def where(self, date_, insee):
        return f"code_zone='{insee}' AND date_ech >= CURRENT_DATE - INTERVAL '3' day"

    def get_from_scraping(self, previous_results, date_, insee):
        r = requests.get(f'https://www.atmo-auvergnerhonealpes.fr/monair/commune/{insee}')
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        controls = soup.find_all('div', class_='day-controls')
        days = controls[0].find_all('a', class_='raster-control-link')

        return [
            self.getter({
                "date": str(datetime.fromtimestamp(int(day.attrs.get('data-rasterid'))).date()),
                "indice": int(int(day.attrs.get('data-index'))/10),
            })
            for day in days
        ]


class Episode(Service, EpisodeMixin):
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/Episodes%20de%20pollution%20pr%C3%A9vus%20ou%20constat%C3%A9s/FeatureServer/0/query'
