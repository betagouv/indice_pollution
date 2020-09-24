from importlib import import_module
from itertools import chain
import requests
import logging

regions = [
    'Auvergne-Rhône-Alpes',
    'Bretagne',
    'Corse',
    'Pays de la Loire',
    'Centre-Val de Loire',
    'Nouvelle-Aquitaine',
    'Hauts-de-France',
    'Grand Est',
    'Occitanie',
    'Île-de-France',
    'Sud',
    'Normandie'
]

def insee_list():
    return list(chain(*[
        import_module(f'.{region_name}', 'indice_pollution.regions').Forecast().insee_list
        for region_name in regions
    ]))

def get_region_name(insee):
    try:
        insee = f'{int(insee):05}'
    except ValueError:
        pass

    r = requests.get(f'https://geo.api.gouv.fr/communes/{insee}', params={"fields": "region"})
    r.raise_for_status()
    return r.json()['region']['nom']

def region(insee=None, region_name=None):
    region_name = region_name or get_region_name(insee)
    try:
        region = import_module(f'.{region_name}', 'indice_pollution.regions')
    except ModuleNotFoundError as e:
        logging.error(f'Region {region_name} not found INSEE: {insee}')
        logging.error(e)
        raise KeyError

    return region