from . import ServiceMixin, ForecastMixin, EpisodeMixin

class Service(ServiceMixin):
    is_active = True
    website =  'https://www.qualitaircorse.org/'
    nom_aasqa = 'Qualitair Corse'
    #insee_list = ['2B033', '2A004', '2B096']

class Forecast(Service, ForecastMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/indice_atmo_communal_corse/FeatureServer/0/query'

    def params(self, date_, insee):
        return {
            "outFields": "*",
            "outSR": "4326",
            "f":"json",
            "where": f"code_zone='{insee}'",
            'orderByFields': 'date_ech DESC',
            'resultRecordCount': 3
        }

class Episode(Service, EpisodeMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/Alrt3j_corse/FeatureServer/0/query'