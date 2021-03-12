from . import ServiceMixin, ForecastMixin, EpisodeMixin

class Service(ServiceMixin):
    website =  'https://www.qualitaircorse.org/'
    nom_aasqa = 'Qualitair Corse'
    insee_list = ['2B096', '2B033', '2A004']

class Forecast(Service, ForecastMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/indice_atmo_communal_corse/FeatureServer/0/query'

    def params(self, date_, insee):
        return {
            "outFields": "date_ech,code_qual,lib_qual,coul_qual,code_zone,lib_zone,code_no2,code_so2,code_o3,code_pm10,code_pm25",
            "outSR": "4326",
            "f":"json",
            "where": f"code_zone='{insee}' AND date_ech>='{date_}'"
        }

class Episode(Service, EpisodeMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/Alrt3j_corse/FeatureServer/0/query'