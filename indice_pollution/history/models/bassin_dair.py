from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from indice_pollution.extensions import db

class BassinDAir(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    code = Column(String)
    zone_id = Column(Integer, ForeignKey("indice_schema.zone.id"))
    zone = relationship("indice_pollution.history.models.zone.Zone", foreign_keys=zone_id)