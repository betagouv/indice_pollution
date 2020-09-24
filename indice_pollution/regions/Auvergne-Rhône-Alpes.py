from . import ForecastMixin

class Forecast(ForecastMixin):
    website = 'https://www.atmo-auvergnerhonealpes.fr/'
    url = 'https://services3.arcgis.com/o7Q3o5SkiSeZD5LK/arcgis/rest/services/ind_atmo_aura/FeatureServer/0/query'
    
    insee_list = [
        '73065', '74081', '43157', '69123', '73248', '03190', '74012', '38544', '73011',
        '63300', '01053', '74056', '03310', '03185', '42187', '15014', '38185', '74010',
        '42218', '26362', '38053', '01328', '63113'
    ]
