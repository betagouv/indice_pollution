from . import ForecastMixin
from datetime import datetime, timedelta
from dateutil.parser import parse
import requests
from flask import current_app

class Forecast(ForecastMixin):
    website = 'https://www.airparif.asso.fr/'
    url = 'https://services8.arcgis.com/gtmasQsdfwbDAQSQ/arcgis/rest/services/ind_idf_agglo/FeatureServer/0/query'

    insee_list = ['75056']

    def where(self, date_, insee):
        return f"date_ech >= CURRENT_DATE - INTERVAL '2' DAY"
    
    def get_close_insee(self, insee):
        return insee