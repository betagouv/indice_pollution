from importlib import import_module
from indice_pollution.history.models.commune import Commune
import logging

def get_region(insee=None, region_name=None):
    if not region_name and insee:
        commune = Commune.get(insee).departement.region.nom
        if commune.departement and commune.departement.region:
            return commune.departement.region.nom
        logging.error(f"No region for {insee}")
        raise KeyError
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