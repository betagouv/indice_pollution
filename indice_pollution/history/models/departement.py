from indice_pollution.extensions import db
from indice_pollution.history.models.region import Region
from indice_pollution.history.models.tncc import TNCC
from sqlalchemy.orm import relation, relationship
import requests

class Departement(db.Model, TNCC):
    __table_args__ = {"schema": "indice_schema"}
    __tablename__ = 'departement'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)
    code = db.Column(db.String)
    region_id = db.Column(db.Integer, db.ForeignKey('indice_schema.region.id'))
    region = relationship("indice_pollution.history.models.region.Region")
    preposition = db.Column(db.String)
    zone_id = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'))
    zone = relationship("indice_pollution.history.models.zone.Zone")

    def __init__(self, **kwargs):
        if 'codeRegion' in kwargs:
            self.region = Region.get(kwargs.pop('codeRegion'))
        super().__init__(**kwargs)

    @classmethod
    def get(cls, code):
        return db.session.query(cls).filter_by(code=code).first() or cls.get_and_init_from_api(code)

    @classmethod
    def get_and_init_from_api(cls, code):
        res_api = cls.get_from_api(code)

        r = cls(**res_api)
        db.session.add(r)
        db.session.commit()
        return r

    @classmethod
    def get_from_api(cls, code):
        r = requests.get(
            f'https://geo.api.gouv.fr/departements/{code}?fields=nom,code,codeRegion',
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        return r.json()