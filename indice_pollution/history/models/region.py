from indice_pollution.extensions import db
import requests

class Region(db.Model):
    __table_args__ = {"schema": "indice_schema"}
    __tablename__ = 'region'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)
    code = db.Column(db.String)

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