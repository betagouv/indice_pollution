from indice_pollution.history.models.region import Region
from indice_pollution.models import db
from indice_pollution.history.models.departement import Departement
from sqlalchemy.orm import relationship
import requests
import json
from flask import current_app

class Commune(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    insee = db.Column(db.String)
    nom = db.Column(db.String)
    departement_id = db.Column(db.Integer, db.ForeignKey("indice_schema.departement.id"))
    departement = relationship("indice_pollution.history.models.departement.Departement")
    code_zone = db.Column(db.String)
    _centre = db.Column('centre', db.String)

    def __init__(self, nom, codeDepartement, centre, code):
        self.nom = nom
        self.insee = code
        self.departement = Departement.get(codeDepartement)
        self.centre = centre

    @property
    def centre(self):
        return json.loads(self._centre)

    @centre.setter
    def centre(self, value):
        self._centre = json.dumps(value)

    @classmethod
    def get(cls, insee):
        return db.session.query(cls).filter_by(insee=insee).first() or cls.get_and_init_from_api(insee)

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
                "fields": "code,nom,codeDepartement,centre",
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

        return r.json()