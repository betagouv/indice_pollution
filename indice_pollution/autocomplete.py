import requests
from .regions.solvers import insee_list

def autocomplete(query_string):
    headers = {
        'Accept': 'application/json'
    }
    params = {
        'nom': query_string,
        'fields': 'nom,code,codesPostaux',
        'format': 'json',
        'boost': 'population'
    }
    r = requests.get(
        "https://geo.api.gouv.fr/communes",
        params=params,
        headers=headers
    )

    r.raise_for_status()

    insee_list_cache = insee_list()
    return list(filter(
        lambda v: v['code'] in insee_list_cache,
        r.json()
    ))