from sqlalchemy.orm import relationship
from indice_pollution.extensions import db

class BassinDAir(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)
    code = db.Column(db.String)
    zone_id = db.Column(db.Integer, db.ForeignKey("indice_schema.zone.id"))
    zone = relationship("indice_pollution.history.models.zone.Zone", foreign_keys=zone_id)