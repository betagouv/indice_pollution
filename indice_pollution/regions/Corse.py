from . import ForecastMixin

class Forecast(ForecastMixin):
    website =  'https://www.qualitaircorse.org/'
    url = 'https://services9.arcgis.com/VQopoXNvUqHYZHjY/arcgis/rest/services/ind_atmo_corse/FeatureServer/0/query'


    @classmethod
    def params(cls, date_, insee):
        return {
            'where': f"(date_ech >= '{date_}') AND (code_zone='{insee}')",
            'outFields': ",".join(cls.outfields),
            'f': 'json',
            'outSR': '4326'
        }    insee_list = ['2B096', '2B033', '2A004']