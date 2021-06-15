from . import ServiceMixin, ForecastMixin, EpisodeMixin
from indice_pollution.history.models import Zone

class Service(ServiceMixin):
    is_active = True
    website = 'http://www.atmo-grandest.eu/'
    nom_aasqa = 'ATMO Grand Est'
    insee_list = [
        '8105', '57463', '67180', '67482', '88160', '57672', '10387', '68224', '68297',
        '57227', '68066', '52448', '51454', '54395', '51108'
    ]

class Forecast(Service, ForecastMixin):
    url = 'https://services3.arcgis.com/Is0UwT37raQYl9Jj/arcgis/rest/services/ind_grandest_4j/FeatureServer/0/query'
    outfields = ['*']

    @classmethod
    def get_zone(cls, properties):
        int_code = properties['code_zone']
        code = f"{int_code:05}"
        return Zone.get(code=code, type_=properties['type_zone'].lower())

class Episode(Service, EpisodeMixin):
    url = 'https://services3.arcgis.com/Is0UwT37raQYl9Jj/arcgis/rest/services/alrt3j_grandest/FeatureServer/0/query'