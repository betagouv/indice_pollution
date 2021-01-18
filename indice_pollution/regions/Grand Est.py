from . import ServiceMixin, ForecastMixin, EpisodeMixin

class Service(ServiceMixin):
    website = 'http://www.atmo-grandest.eu/'
    insee_list = [
        '8105', '57463', '67180', '67482', '88160', '57672', '10387', '68224', '68297',
        '57227', '68066', '52448', '51454', '54395', '51108'
    ]

class Forecast(Service, ForecastMixin):
    url = 'https://services3.arcgis.com/Is0UwT37raQYl9Jj/arcgis/rest/services/ind_grandest_5j/FeatureServer/0/query'
    outfields = ['*']

class Episode(Service, EpisodeMixin):
    url = 'https://services3.arcgis.com/Is0UwT37raQYl9Jj/arcgis/rest/services/alrt3j_grandest/FeatureServer/0/query'