from indice_pollution.history.models.commune import Commune
import requests
import logging
import time
import pytz
import json
import unidecode
from datetime import datetime
from dateutil import parser as dateutil_parser
from sqlalchemy import exc
from indice_pollution.history.models import IndiceHistory, EpisodeHistory
from indice_pollution.models import db

class ServiceMixin(object):
    is_active = True
    url = ""
    epci_list = []
    insee_epci = dict()
    outfields = ['date_ech', 'valeur', 'qualif', 'val_no2', 'val_so2',
     'val_o3', 'val_pm10', 'val_pm25'
    ]

    attributes_key = 'attributes'
    use_dateutil_parser = False
    get_only_from_scraping = False

    HTTPAdapter = requests.adapters.HTTPAdapter

    def get_one_attempt(self, url, params):
        s = requests.Session()
        s.mount('https://', self.HTTPAdapter())
        try:
            r = s.get(url, params=params)
        except requests.exceptions.ConnectionError as e:
            logging.error(f'Impossible de se connecter à {url}')
            logging.error(e)
            return None
        except requests.exceptions.SSLError as e:
            logging.error(f'Erreur ssl {url}')
            logging.error(e)
            return None
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.error(f'Erreur HTTP dans la requete {url} {params}: {e}')
            return None
        try:
            if 'error' in r.json():
                logging.error(f'Erreur dans la réponse à la requête: {url} {params}: {r.json()}')
                return None
        except ValueError:
            pass
        return r

    def get_multiple_attempts(self, url, params, attempts=0):
        r = self.get_one_attempt(url, params)
        if r:
            features = self.features(r)
            if not features and 'error' in r.text:
                logging.error(f'Errors in response: {r.text}')
        else:
            features = []
        if attempts >= 1 or len(features) > 0:
            return features
        else:
            time.sleep(0.5 * (attempts + 1))
            return self.get_multiple_attempts(url, params, attempts+1)

    def get(self, date_, insee, attempts=0, force_from_db=False):
        to_return = []
        try:
            insee = self.get_close_insee(insee)
        except KeyError:
            return []
        if force_from_db:
            indice = self.HistoryModel.get(date_, insee)
            if indice:
                return [indice.features]
        if not to_return:
            to_return = self.HistoryModel.get_after(date_, insee)
        if not to_return and not self.get_only_from_scraping:
            to_return = self.get_no_cache(date_, insee, attempts)
        if not any(map(lambda r: (r['date'] if 'date' in r else r['date_dif']) == str(date_), to_return)):
            if hasattr(self, "get_from_scraping"):
                to_return = self.get_from_scraping(to_return, date_, insee)
        to_return = list(filter(lambda r: r['date']>= str(date_), to_return))
        if to_return:
            for v in to_return:
                indice = self.HistoryModel.get_or_create(v['date'], insee, features=v)
                db.session.commit()
        else:
            logging.error(f"Pas d’épisode de pollution pour '{insee}'")
        return to_return

    def get_no_cache(self, date_, insee, attempts=0):
        features = self.get_multiple_attempts(self.url, self.params(date_, insee), attempts)
        return list(filter(lambda s: s is not None, map(lambda f: self.getter(self.attributes_getter(f)), features)))

    def features(self, r):
        try:
            return r.json()['features']
        except json.decoder.JSONDecodeError:
            logging.error(f'Unable to decode JSON "{r.text}"')
        except KeyError as e:
            logging.error(f'Unable to find key "features" in "{r.json().keys()}"')
        return []

    @property
    def insee_list(self):
        return [] if not self.insee_epci else self.insee_epci.keys()

    def get_close_insee(self, insee):
        if insee in self.insee_list or self.insee_list == []:
            return insee
        commune = Commune.get(insee)
        try:
            return next(pref_insee for pref_insee in self.insee_list if pref_insee[:2] == commune.departement.code)
        except StopIteration:
            logging.error(f'Impossible de trouver le code insee de la préfecture de {insee}')
            raise KeyError

    def attributes_getter(self, feature):
        try:
            return feature[self.attributes_key]
        except KeyError as e:
            logging.error(f"KeyError dans attributes getter self.attributes_key: '{self.attributes_key}' keys: '{feature.keys()}'")
            raise e


    def date_getter(self, attributes):
        str_date = attributes.get('date_ech', attributes.get('date'))
        if not str_date:
            return
        if not self.use_dateutil_parser and type(str_date) == int:
            zone = pytz.timezone('Europe/Paris')
            return datetime.fromtimestamp(str_date/1000, tz=zone)
        else:
            try:
                return dateutil_parser.parse(str_date)
            except dateutil_parser.ParserError as e:
                logging.error(f'Unable to parse date: "{str_date}"')
                logging.error(e)
                return

class ForecastMixin(ServiceMixin):
    HistoryModel = IndiceHistory
    outfields = ['date_ech', 'valeur', 'qualif', 'val_no2', 'val_so2',
     'val_o3', 'val_pm10', 'val_pm25'
    ]

    def where(self, date_, insee):
        zone = insee if not self.insee_epci else self.insee_epci[insee]
        return f"(date_ech >= '{date_}') AND (code_zone='{zone}')"

    def params(self, date_, insee):
        return {
            'where': self.where(date_, insee),
            'outFields': ",".join(self.outfields),
            'f': 'json',
            'outSR': '4326'
        }

    def getter(self, attributes):
        dt = self.date_getter(attributes)
        qualif = self.indice_getter(attributes)
        label = self.label_getter(qualif)
        couleur = self.couleur_getter(attributes, qualif)

        return {
            'indice': qualif,
            'label': label,
            'couleur': couleur,
            'sous_indices': attributes.get('sous_indices'),
            'date': str(dt.date()),
            **{k: attributes[k] for k in self.outfields if k in attributes}
        }

    def indice_getter(self, attributes):
        # On peut avoir un indice à 0, ce qui nous empêche de faire
        # indice = attributes.get('indice) or attributes.get('valeur)
        # car attributes.get('indice') sera truthy
        indice = attributes.get('indice', attributes.get('valeur'))
        # De même, on peut avoir indice valant 0
        # ce qui nous empêche de faire
        # if indice:
        if indice != None:
            if type(indice) == int:
                return {
                    0: "bon",
                    1: "moyen",
                    2: "degrade",
                    3: "mauvais",
                    4: "tres_mauvais",
                    5: "extrememen_mauvais",
                }.get(indice)
            if type(indice) == str:
                # Certaines régions mettent des accents, d’autres pas
                # On désaccentue tout
                return unidecode.unidecode(indice).strip()
            return indice.strip()
        if 'lib_qual' in attributes:
            return {
                "Très bon": "bon", # retrocompatiblité
                "Bon": "bon",
                "Moyen": "moyen",
                "Dégradé": "degrade",
                "Mauvais": "mauvais",
                "Très mauvais": "tres_mauvais",
                "Extrêment mauvais": "extrement_mauvais",
            }.get(attributes['lib_qual'])


    def label_getter(self, indice):
        if not indice:
            return
        return {
            "tres_bon": "Très bon", #On garde la rétro compatibilité pour l’instant
            "bon": "Bon",
            "moyen": "Moyen",
            "degrade": "Dégradé",
            "mauvais": "Mauvais",
            "mediocre": "Médiocre", #On garde la rétro compatibilité pour l’instant
            "tres_mauvais": "Très mauvais",
            "extrement_mauvais": "Extrêment mauvais",
        }.get(
            indice.lower().strip(),
            indice.strip()
        )

    def couleur_getter(self, attributes, indice):
        couleur = attributes.get('couleur') or attributes.get('coul_qual')
        if couleur:
            return couleur
        if not indice:
            return
        return {
            "tres_bon": "#50F0E6", #On garde la rétro-compatibilité
            "bon": "#50F0E6",
            "moyen": "#50CCAA",
            "degrade": "#F0E641",
            "mediocre": "#F0E641", #On garde la rétro-compatibilité
            "mauvais": "#FF5050",
            "tres_mauvais": "#960032",
            "extrement_mauvais": "#960032",
        }.get(
            indice.lower()
        )


class EpisodeMixin(ServiceMixin):
    HistoryModel = EpisodeHistory
    outfields = ['date_ech', 'lib_zone', 'code_zone', 'date_dif', 'code_pol',
     'lib_pol', 'etat', 'com_court', 'com_long']
    
    def getter(self, attributes):
        try:
            date_ech = self.date_getter(attributes)
        except KeyError as e:
            logging.error(f"Unable to get key 'date_ech' or 'date_dif' in {attributes.keys()}")
            logging.error(e)
            return
        if not date_ech:
            return

        return {
            'date': str(date_ech.date()),
            **{k: attributes[k] for k in self.outfields if k in attributes},
        }

    def centre(self, insee):
        r = requests.get(
            f'https://geo.api.gouv.fr/communes/{insee}',
            params={"fields": "centre", "format": "json", "geometry": "centre"}
        )
        r.raise_for_status()
        return r.json()['centre']['coordinates']

    def params(self, date_, insee):
        centre = self.centre(insee)

        return {
            'where': '',
            'outfields': self.outfields,
            'f': 'json',
            'geometry': f'{centre[0]},{centre[1]}',
            'inSR': '4326',
            'outSR': '4326',
            'geometryType': 'esriGeometryPoint'
        }

    def filtre_post_get(self, code_zone, date_):
        return lambda f: f.get('code_zone') == code_zone and f.get('date') == str(date_)

    def get(self, date_, insee, attempts=0, force_from_db=False):
        commune = Commune.get(insee)
        return list(filter(
            self.filtre_post_get(commune.departement.code, date_),
            super().get(date_, insee, attempts=attempts, force_from_db=force_from_db)
        ))
