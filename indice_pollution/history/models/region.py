from sqlalchemy.orm import relationship
from indice_pollution.extensions import db
import requests
from indice_pollution.history.models.tncc import TNCC

class Region(db.Model, TNCC):
    __table_args__ = {"schema": "indice_schema"}
    __tablename__ = 'region'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)
    code = db.Column(db.String)
    aasqa_website = db.Column(db.String)
    aasqa_nom = db.Column(db.String)
    zone_id = db.Column(db.Integer, db.ForeignKey("indice_schema.zone.id"))
    zone = relationship("indice_pollution.history.models.zone.Zone")

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
        r = requests.get(f'https://geo.api.gouv.fr/regions/{code}?fields=nom,code')
        r.raise_for_status()
        return r.json()