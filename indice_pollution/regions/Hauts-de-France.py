from . import ForecastMixin
from datetime import timedelta
from dateutil.parser import parse

class Forecast(ForecastMixin):
    date_format = '%Y-%m-%d'
    website = 'https://www.atmo-hdf.fr/'
    url = 'https://services8.arcgis.com/rxZzohbySMKHTNcy/arcgis/rest/services/ind_hdf_agglo/FeatureServer/0/query'

    insee_list = [
        '59350', '59183', '59178', '62041', '62160', '59606', '02691', '60175',
        '62765', '62193', '59392', '80021', '62119'
    ]