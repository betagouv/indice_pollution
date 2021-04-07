from importlib import import_module
from indice_pollution.history.models.commune import Commune
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

def get_region(insee=None, region_name=None):
    if not region_name and insee:
        region_name = Commune.get(insee).departement.region.nom
    if not region_name:
        logging.error("No region or insee given, couldn't find region")
        raise KeyError
    try:
        region = import_module(f'.{region_name}', 'indice_pollution.regions')
    except ModuleNotFoundError as e:
        logging.error(f'Region {region_name} not found INSEE: {insee}')
        logging.error(e)
        raise KeyError

    return region