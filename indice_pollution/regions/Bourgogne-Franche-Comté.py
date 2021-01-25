from . import EpisodeMixin, ForecastMixin
import csv
from dateutil.parser import parse
from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta

class Service(object):
    website = 'https://www.atmo-bfc.org/'

    def get_close_insee(self, insee):
        return insee

class Forecast(Service, ForecastMixin):
    url_scraping = 'https://www.atmo-bfc.org/medias/ajax/me_gateway.php'
    url = 'https://atmo-bfc.iad-informatique.com/geoserver/indice/ows'
    attributes_key = 'properties'
    use_dateutil_parser = True

    def params(self, date_, insee):
        return {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': f'indice:vu_indice_bourgogne-franche-comte',
            'outputFormat': 'application/json',
            'CQL_FILTER': f"date_ech >= '{date_}T00:00:00Z' AND code_zone={insee}"
        }


    def get_from_scraping_one_day(self, params):
        r = requests.post(self.url_scraping,
            headers={
                'Accept-Encoding': '*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data=params
        )
        r.raise_for_status()
        return r

    def params_scraping(self, date_, insee):
        self.date_ = date_
        return {
            "meC": "abo_communes",
            "meM": "traitementAjax",
            "meIdC": "7448b8180480a8749b31941011165d92.MTQxNQ%3D%3D",
            "meT": "i",
            "paramsM[mode]": "refreshCartePolluant",
            "paramsM[meCibleId]": "7448b8180480a8749b31941011165d92_MTQxNQ_3D_3D",
            "paramsM[meDate]": date_,
            "paramsM[codeCommune]": insee,
            "paramsM[idPolluant]": -1,
            "paramsM[codeAgglo]": 3,
            "paramsM[changeJour]": 1,
            "paramsM[prevPolluant]": 0,
            "m_idPage": 183,
            "m_initialesLangue": "fr",
            "ajax": 1
        }

    def get_from_scraping(self, previous_results, date_, insee):
        if insee not in self.insee_list:
            insee = self.get_close_insee(insee)
        day_before = str((date_ - timedelta(days=1)))
        day_after = str((date_ + timedelta(days=1)))
        features_daybefore = self.features_scraping(self.get_from_scraping_one_day(self.params_scraping(day_before, insee)))
        features_date = self.features_scraping(self.get_from_scraping_one_day(self.params_scraping(str(date_), insee)))
        features_dayafter = self.features_scraping(self.get_from_scraping_one_day(self.params_scraping(day_after, insee)))
        return [
            f
            for f in [
                features_daybefore,
                features_date,
                features_dayafter
            ]
            if f
        ]

    def features_scraping(self, r):
        if not "indices" in r.json():
            return []
        soup = BeautifulSoup(r.json()["indices"], features="html5lib")
        valeurIndice = soup.find_all("div", class_="valeurIndice")[0]
        return {
            "indice": valeurIndice.find_all("span")[1].text,
            "date": self.date_
        }

class Episode(Service, EpisodeMixin):
    url = 'http://atmo-bfc.iad-informatique.com/geoserver/alerte/wfs'
    attributes_key = 'properties'

    def params(self, date_, insee):
        centre = self.centre(insee)

        return {
            'where': '',
            'outfields': self.outfields,
            'outputFormat': 'application/json',
            'geometry': f'{centre[0]},{centre[1]}',
            'inSR': '4326',
            'outSR': '4326',
            'geometryType': 'esriGeometryPoint',
            'request': 'GetFeature',
            'typeName': 'alerte:alrt3j_bfc'
        }

    def getter(self, attributes):
        return super().getter({'code_pol': attributes['id_poll_ue'], **attributes})