from . import ServiceMixin, ForecastMixin, EpisodeMixin

class Service(ServiceMixin):
    is_active = True
    website =  'https://www.qualitaircorse.org/'
    nom_aasqa = 'Qualitair Corse'

class Forecast(Service, ForecastMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/indice_atmo_communal_corse/FeatureServer/0/query'

    @property
    def params_fetch_all(self):
        return {
            "outFields": "*",
            "outSR": "4326",
            "f":"json",
            'orderByFields': 'date_ech DESC',
            'where': "(date_ech >= CURRENT_DATE - INTERVAL '5' DAY)",
        }

class Episode(Service, EpisodeMixin):
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/Alrt3j_corse/FeatureServer/0/query'