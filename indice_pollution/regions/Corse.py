from . import ForecastMixin

class Forecast(ForecastMixin):
    website =  'https://www.qualitaircorse.org/'
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/ind_atmo_corse/FeatureServer/0/query'

    insee_list = ['2B096', '2B033', '2A004']