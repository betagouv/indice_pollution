from indice_pollution.models import db
from sqlalchemy.orm import relationship
from indice_pollution.history.models import Commune

class EPCI(db.Model):
    __table_args__ = {"schema": "indice_schema"}
    __tablename__ = "epci"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String())
    label = db.Column(db.String())
    departement_id = db.Column(db.Integer, db.ForeignKey("indice_schema.departement.id"))
    departement = relationship("indice_pollution.history.models.departement.Departement")
    zone_id = db.Column(db.Integer, db.ForeignKey("indice_schema.zone.id"))
    zone = relationship("indice_pollution.history.models.zone.Zone")

    @classmethod
    def get(cls, code=None, insee=None):
        return cls.get_query(code, insee).first()

    @classmethod
    def get_query(cls, code=None, insee=None):
        if code:
            return cls.query.filter_by(code=code)
        if insee:
            subquery = Commune.get_query(insee).with_entities(Commune.epci_id).subquery()
            return cls.query.filter(cls.id==subquery)