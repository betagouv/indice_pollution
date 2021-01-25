from indice_pollution.models import db
import requests
import json

class Commune(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    insee = db.Column(db.String)
    nom = db.Column(db.String)
    code_departement = db.Column(db.String)
    code_region = db.Column(db.String)
    code_zone = db.Column(db.String)
    nom_region = db.Column(db.String)
    _centre = db.Column('centre', db.String)

    @property
    def centre(self):
        return json.loads(self._centre)

    @centre.setter
    def centre(self, value):
        self._centre = json.dumps(value)

    @classmethod
    def get(cls, insee):
        result = db.session.query(cls).filter_by(insee=insee).first()
        if result:
            return result
        r = requests.get(
            f'https://geo.api.gouv.fr/communes/{insee}',
            params={
                "fields": "code,nom,codeDepartement,region,centre",
                "format": "json",
            }
        )
        r.raise_for_status()

        o = cls(
            insee=insee,
            nom=r.json()['nom'],
            code_departement=r.json()['codeDepartement'],
            code_region=r.json()['region']['code'],
            nom_region=r.json()['region']['nom'],
            centre=r.json()['centre']
        )
        db.session.add(o)
        db.session.commit()
        return o