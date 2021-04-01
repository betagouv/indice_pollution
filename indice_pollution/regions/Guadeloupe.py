from indice_pollution.regions import EpisodeMixin, ServiceMixin, ForecastMixin

class Service(ServiceMixin):
    is_active = True
    website = 'http://www.gwadair.fr//'
    nom_aasqa = "Gwad'Air"

class Forecast(Service, ForecastMixin):
    url = 'https://services8.arcgis.com/7RrxpwWeFIQ8JGGp/arcgis/rest/services/ind_guadeloupe_1/FeatureServer/0/query'
    outfields = ['*']

class Episode(Service, EpisodeMixin):
    url = 'https://services8.arcgis.com/7RrxpwWeFIQ8JGGp/arcgis/rest/services/alrt3j_guadeloupe_1/FeatureServer/0/query'
    outfields = ['*']