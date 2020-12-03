from sqlalchemy.sql.elements import _corresponding_column_or_error
from indice_pollution.models import db
import json
from .commune import Commune

class EpisodeHistory(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    date_ = db.Column(db.Date, nullable=False)
    code_departement = db.Column(db.String, nullable=False)
    _features = db.Column("features", db.String, nullable=False)

    def __init__(self, date_, insee=None, code_departement=None) -> None:
        code_departement = code_departement or Commune.get(insee).code_departement
        super().__init__(date_=date_, code_departement=code_departement)

    @property
    def features(self):
        return json.loads(self._features)

    @features.setter
    def features(self, value):
        self._features = json.dumps(value)

    @classmethod
    def get(cls, date_, insee=None, code_departement=None):
        code_departement = code_departement or Commune.get(insee).code_departement
        return db.session.query(cls).filter_by(date_=date_, code_departement=code_departement).first()
    
    @classmethod
    def get_bulk(cls, date_, insee_list):
        insee_list = set(insee_list)
        insee_code_departement_list = [
            (c.insee, c.code_departement)
            for c in Commune.query.filter(Commune.insee.in_(insee_list))
        ]
        diff = insee_list - set([c[0] for c in insee_code_departement_list])
        if len(diff) > 0:
            for insee in diff:
                commune = Commune.get(insee)
                insee_code_departement_list.append(
                    (commune.insee, commune.code_departement)
                )
        code_departement_list = [c[1] for c in insee_code_departement_list]

        return cls.query\
            .filter(cls.date_==date_, cls.code_departement.in_(set(code_departement_list)))\
            .all()

    @classmethod
    def get_after(cls, date_, insee):
        commune = Commune.get(insee)
        return [v.features for v in cls.query.filter(cls.date_ >= date_, cls.code_departement==commune.code_departement).all()]

    @classmethod
    def get_or_create(cls, date_, insee=None, code_departement=None):
        code_departement = code_departement or Commune.get(insee).code_departement
        result =  cls.get(date_, code_departement=code_departement)
        if result:
            return result
        result = cls(date_=date_, code_departement=code_departement)
        db.session.add(result)
        return result