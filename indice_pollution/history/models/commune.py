from indice_pollution.extensions import db
from indice_pollution.history.models.departement import Departement
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
import requests
import json
from flask import current_app

class Commune(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    insee = db.Column(db.String)
    nom = db.Column(db.String)
    epci_id = db.Column(db.Integer, db.ForeignKey("indice_schema.epci.id"))
    epci = relationship("indice_pollution.history.models.epci.EPCI")
    departement_id = db.Column(db.Integer, db.ForeignKey("indice_schema.departement.id"))
    departement = relationship("indice_pollution.history.models.departement.Departement")
    code_zone = db.Column(db.String)
    zone_id = db.Column(db.Integer, db.ForeignKey("indice_schema.zone.id"))
    zone = relationship("indice_pollution.history.models.zone.Zone", foreign_keys=zone_id)
    _centre = db.Column('centre', db.String)
    zone_pollution_id = db.Column(db.Integer, db.ForeignKey("indice_schema.zone.id"))
    zone_pollution = relationship("indice_pollution.history.models.zone.Zone", foreign_keys=zone_pollution_id)
    pollinarium_sentinelle = db.Column(db.Boolean)
    codes_postaux = db.Column(postgresql.ARRAY(db.String))

    def __init__(self, **kwargs):
        if 'code' in kwargs:
            kwargs['insee'] = kwargs.pop('code')
        if 'codeDepartement' in kwargs:
            kwargs['departement'] = Departement.get(kwargs.pop('codeDepartement'))
        super().__init__(**kwargs)

    @property
    def centre(self):
        return json.loads(self._centre)

    @centre.setter
    def centre(self, value):
        self._centre = json.dumps(value)

    @classmethod
    def get(cls, insee):
        if insee is None:
            return None
        return cls.get_query(insee).first() or cls.get_and_init_from_api(insee)

    @classmethod
    def get_query(cls, insee=None, code=None):
        if insee:
            return db.session.query(cls).filter_by(insee=insee).limit(1)
        elif code:
            from indice_pollution.history.models.epci import EPCI
            subquery = EPCI.get_query(code=code).with_entities(EPCI.id).limit(1).subquery()
            return cls.query.filter(cls.epci_id==subquery).limit(1)

    @classmethod
    def bulk_query(cls, insees=None, codes=None):
        if insees:
            return db.session.query(cls).filter(cls.insee.in_(insees))
        elif codes:
            from indice_pollution.history.models.epci import EPCI
            subquery = EPCI.bulk_query(codes=codes).with_entities(EPCI.id).subquery()
            return cls.query.filter(cls.epci_id.in_(subquery)).limit(1)

    @classmethod
    def get_and_init_from_api(cls, insee):
        res_api = cls.get_from_api(insee)
        if not res_api:
            return None
        o = cls(**res_api)
        db.session.add(o)
        db.session.commit()
        return o

    @classmethod
    def get_from_api(cls, insee):
        r = requests.get(
            f'https://geo.api.gouv.fr/communes/{insee}',
            params={
                "fields": "code,nom,codeDepartement,centre,codesPostaux",
                "format": "json",
            }
        )
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            current_app.logger.error(f"HTTP Error getting commune: '{insee}' {e}")
            return None
        if not 'codeDepartement' in r.json() or not 'centre' in r.json():
            current_app.logger.error(f'Error getting info about: "{insee}" we need "codeDepartement" and "centre" in "{r.json()}"')
            return None
        j = r.json()
        if 'codesPostaux' in j:
            j['codes_postaux'] = j['codesPostaux']
            del j['codesPostaux']
        return j

    @property
    def code(self):
        return self.insee