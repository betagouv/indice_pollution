from . import ServiceMixin, ForecastMixin, EpisodeMixin
from datetime import timedelta
from dateutil.parser import parse

class Service(ServiceMixin):
    date_format = '%Y-%m-%d'
    website = 'https://www.atmo-hdf.fr/'

class Forecast(Service, ForecastMixin):
    url = 'https://services8.arcgis.com/rxZzohbySMKHTNcy/arcgis/rest/services/ind_hdf_2021/FeatureServer/0/query'
    outfields = '*'

class Episode(Service, EpisodeMixin):
    url = 'https://services8.arcgis.com/rxZzohbySMKHTNcy/arcgis/rest/services/alrt3j_hdf/FeatureServer/0/query'