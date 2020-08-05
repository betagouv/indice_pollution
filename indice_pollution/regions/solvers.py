from importlib import import_module
from itertools import chain
import requests

regions = [
    'Auvergne-Rhône-Alpes',
    'Bretagne',
    'Corse',
    'Pays de la Loire',
    'Centre-Val de Loire',
    'Nouvelle-Aquitaine',
    'Hauts-De-France',
    'Grand Est',
    'Occitanie',
    'Île-de-France',
    'Sud',
    'Normandie'
]

def insee_list():
    return list(chain(*[
        import_module(f'.{region_name}', 'indice_pollution.regions').Forecast.insee_list()
        for region_name in regions
    ]))

def forecast(insee):
    r = requests.get(f'https://geo.api.gouv.fr/communes/{insee}', params={"fields": "region"})
    r.raise_for_status()
    region_name = r.json()['region']['nom']
    region = import_module(f'.{region_name}', 'indice_pollution.regions').Forecast()

    return region.get