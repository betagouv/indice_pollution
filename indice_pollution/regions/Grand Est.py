from . import ForecastMixin

class Forecast(ForecastMixin):
    website = 'http://www.atmo-grandest.eu/'
    url = 'https://services3.arcgis.com/Is0UwT37raQYl9Jj/arcgis/rest/services/ind_Grand_Est_commune_3j/FeatureServer/0/query'

    insee_list = [
        '8105', '57463', '67180', '67482', '88160', '57672', '10387', '68224', '68297',
        '57227', '68066', '52448', '51454', '54395', '51108'
    ]

    @classmethod
    def params(cls, date_, insee):
        return {
            'f': 'json',
            'outFields': ",".join(cls.outfields),
            'outSR': '4326',
            'where': f"(code_zone={insee}) AND (date_ech >= DATE '{date_}')"
        }