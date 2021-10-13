import requests
import logging
import time
import pytz
import json
import unidecode
import itertools
from datetime import datetime
from dateutil import parser as dateutil_parser
from sqlalchemy import and_, bindparam, select
from sqlalchemy.dialects.postgresql import Insert, insert as pg_insert
from indice_pollution.history.models import IndiceHistory, EpisodeHistory, IndiceATMO, Zone, Commune, EPCI, EpisodePollution
from indice_pollution.extensions import db

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
            indice = self.DB_OBJECT.get(date_, insee)
            if indice:
                return [indice.features]
        if not to_return and not self.get_only_from_scraping:
            to_return = self.get_no_cache(date_, insee, attempts)
        if not any(map(lambda r: (r['date'] if 'date' in r else r['date_dif']) == str(date_), to_return)):
            if hasattr(self, "get_from_scraping"):
                to_return = self.get_from_scraping(to_return, date_, insee)
        to_return = list(filter(lambda r: r['date']>= str(date_), to_return))
        if to_return:
            indices = filter(lambda v: v, map(self.make_indice_dict, to_return))
            ins = pg_insert(self.DB_OBJECT)\
                .values(list(indices))\
                .on_conflict_do_nothing()
            db.session.execute(ins)
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
        return self.date_parser(attributes.get('date_ech', attributes.get('date')))

    @classmethod
    def date_parser(cls, date_field):
        if not date_field:
            return
        if not cls.use_dateutil_parser and type(date_field) == int:
            zone = pytz.timezone('Europe/Paris')
            return datetime.fromtimestamp(date_field/1000, tz=zone)
        else:
            try:
                return dateutil_parser.parse(date_field)
            except dateutil_parser.ParserError as e:
                logging.error(f'Unable to parse date: "{date_field}"')
                logging.error(e)
                return

    def save_all(self):
        indices = filter(lambda v: v, map(self.make_indice_dict, itertools.chain(*self.fetch_all())))

        def grouper_it(n, iterable):
            it = iter(iterable)
            while True:
                chunk_it = itertools.islice(it, n)
                try:
                    first_el = next(chunk_it)
                except StopIteration:
                    return
                yield itertools.chain((first_el,), chunk_it)
        for chunk in grouper_it(100, indices):
            values = list(chunk)
            ins = pg_insert(self.DB_OBJECT)\
                .values(values)\
                .on_conflict_do_nothing()
            db.session.execute(ins)
        db.session.commit()

    params_fetch_all = {
        'where': '(date_dif >= CURRENT_DATE) OR (date_ech = CURRENT_DATE)',
        'outFields': "*",
        'f': 'json',
        'orderByFields': 'date_ech DESC',
        'outSR': '4326'
    }

    def fetch_all(self):
        url = self.url_fetch_all if hasattr(self, "url_fetch_all") else self.url
        if hasattr(self, 'fetch_only_from_scraping'):
            j =  self.get_from_scraping()
            yield j
        else:
            get_one_attempt = self.get_one_attempt_fetch_all if hasattr(self, "get_one_attempt_fetch_all") else self.get_one_attempt
            response = get_one_attempt(
                url,
                self.params_fetch_all
            )
            if not response:
                yield []
                return
            try:
                j = response.json()
            except json.JSONDecodeError:
                logging.error(f"Unable to decode {url} {self.params_fetch_all}")
                yield []
                return
            yield j['features']
            i = len(j['features'])
            while j.get('exceededTransferLimit'):
                j = get_one_attempt(
                    self.url_fetch_all if hasattr(self, "url_fetch_all") else self.url,
                    {
                        **self.params_fetch_all,
                        **{
                            'resultOffset': i
                        }
                    }
                ).json()
                yield j['features']
                i += len(j['features'])

class ForecastMixin(ServiceMixin):
    outfields = ['date_ech', 'valeur', 'qualif', 'val_no2', 'val_so2',
     'val_o3', 'val_pm10', 'val_pm25'
    ]
    DB_OBJECT = IndiceATMO

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

    @classmethod
    def get_zone_id(cls, properties):
        type_zone = properties.get('type_zone', 'commune').lower()
        code_zone = properties['code_zone'] if type(properties['code_zone']) == str else f"{properties['code_zone']:05}"
        if type_zone == "commune":
            commune = Commune.get(insee=str(code_zone))
            return commune.zone_id if commune else None
        elif type_zone == "epci":
            epci = EPCI.get(code=code_zone)
            return epci.zone_id if epci else None
        return None

    @classmethod
    def make_indice_dict(cls, feature):
        if type(feature) != dict:
            print(feature)
        properties = feature.get('properties') or feature.get('attributes')
        if not 'date_ech' in properties or not 'date_dif' in properties:
            return None
    
        zone_code = properties['code_zone'] if type(properties['code_zone']) == str else f"{properties['code_zone']:05}"
        zone_type = properties.get('type_zone', 'commune').lower()

        if zone_type == "commune":
            sel = select([Commune.zone_id]).where(Commune.insee == zone_code)
        else:
            sel = select([Zone.id]).where(and_(Zone.type==zone_type, Zone.code==zone_code))
        return {
            "zone_id": sel,
            "date_ech" :cls.date_parser(properties['date_ech']),
            "date_dif" :cls.date_parser(properties['date_dif']),
            "no2" :properties.get('code_no2'),
            "so2" :properties.get('code_so2'),
            "o3" :properties.get('code_o3'),
            "pm10" :properties.get('code_pm10'),
            "pm25" :properties.get('code_pm25'),
            "valeur" :properties.get('code_qual') or properties['valeur']
        }

class EpisodeMixin(ServiceMixin):
    DB_OBJECT = EpisodePollution
    zone_type = 'departement'
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

    @classmethod
    def make_indice_dict(cls, feature):
        properties = feature.get('properties') or feature.get('attributes')

        if not properties:
            properties = feature

        date_ech = cls.date_parser(properties.get('date_ech') or properties.get('date'))
        if not date_ech:
            return None
        date_dif = cls.date_parser(properties.get('date_dif'))

        code = properties['code_zone']
        if type(code) == int:
            code = f"{code:02}"

        sel = select(
               [Zone.id]
            ).where(
                and_(
                    Zone.type==cls.zone_type,
                    Zone.code==code
                )
        ) 

        return {
            "zone_id": sel,
            "date_ech" : date_ech,
            "date_dif" : date_dif or date_ech,
            "code_pol" : int(float(properties['code_pol'])),
            "etat" : properties.get('etat'),
            "com_court" : properties.get('com_court'),
            "com_long" : properties.get('com_long'),
        }


    @classmethod
    def get_zone_id(cls, properties):
        code = properties['code_zone']
        if type(code) == int:
            code = f"{code:02}"
        zone = Zone.get(code=code, type_='departement')
        if not zone:
            return 
        return zone.id