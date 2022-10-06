from indice_pollution.regions import EpisodeMixin, ServiceMixin, ForecastMixin
from datetime import date

class Service(ServiceMixin):
    is_active = True
    nom_aasqa = 'ATMO Guyane'
    website = 'https://www.atmo-guyane.org/'
    use_dateutil_parser = True

class Forecast(Service, ForecastMixin):
    url = 'https://dservices8.arcgis.com/5JImMrIjAqUJnR3H/arcgis/services/ind_guyane_nouvel_indice/WFSServer'
    url_fetch_all = 'https://dservices8.arcgis.com/5JImMrIjAqUJnR3H/arcgis/services/ind_guyane_nouvel_indice/WFSServer'

    @classmethod
    def params(cls, date_, insee):
        filter_zone = f'<PropertyIsEqualTo><PropertyName>code_zone</PropertyName><Literal>{insee}</Literal></PropertyIsEqualTo>'
        filter_date_ech = f'<PropertyIsGreaterThanOrEqualTo><PropertyName>date_ech</PropertyName><Literal>{date_}</Literal></PropertyIsGreaterThanOrEqualTo>'
        return {
            'service': 'wfs',
            'version': '2.0.0',
            'request': 'getfeature',
            'typeName': 'ind_guyane_nouvel_indice:ind_guyane_agglo',
            'outputFormat': 'GEOJSON',
            'filter': f"<Filter><And>{filter_zone}{filter_date_ech}</And></Filter>",
        }
    
    @classmethod
    def params_fetch_all(cls):
        filter_date_ech = f'<PropertyIsGreaterThanOrEqualTo><PropertyName>date_ech</PropertyName><Literal>{date.today()}</Literal></PropertyIsGreaterThanOrEqualTo>'
        return {
            'service': 'wfs',
            'version': '2.0.0',
            'request': 'getfeature',
            'typeName': 'ind_guyane_nouvel_indice:ind_guyane_agglo',
            'outputFormat': 'GEOJSON',
            'filter': f"<Filter>{filter_date_ech}</Filter>",
        }

class Episode(Service, EpisodeMixin):
    # API d'Atmo Data
    url = 'https://admindata.atmo-france.org/api/data/114/%7B"code_zone":%7B"operator":"=","value":"973"%7D%7D'
    url_fetch_all = 'https://admindata.atmo-france.org/api/data/114/%7B"code_zone":%7B"operator":"=","value":"973"%7D%7D'

    @classmethod
    def params(cls, date_, insee):
        return {
            'withGeom': 'false', # permet de télécharger les données sans géométrie
        }
    
    @classmethod
    def params_fetch_all(cls):
        return {
            'withGeom': 'false', # permet de télécharger les données sans géométrie
        }