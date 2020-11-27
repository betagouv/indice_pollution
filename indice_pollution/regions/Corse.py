from . import ServiceMixin, ForecastMixin, EpisodeMixin

class Service(ServiceMixin):
    website =  'https://www.qualitaircorse.org/'
    insee_list = ['2B096', '2B033', '2A004']

class Forecast(Service, ForecastMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/ind_atmo_corse/FeatureServer/0/query'

class Episode(Service, EpisodeMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/Alrt3j_corse/FeatureServer/0/query'