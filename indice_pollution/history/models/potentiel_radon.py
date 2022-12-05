from sqlalchemy import Column, ForeignKey, Integer
from indice_pollution.extensions import db
from indice_pollution.history.models.commune import Commune
from dataclasses import dataclass

@dataclass
class PotentielRadon(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    zone_id: int = Column(Integer, ForeignKey('indice_schema.zone.id'), primary_key=True)
    classe_potentiel: int = Column(Integer)

    @classmethod
    def get(cls, insee):
        return cls.query.join(Commune, Commune.zone_id == cls.zone_id).filter(Commune.insee == insee).first()

    @property
    def label(self):
        return f"Catégorie {self.classe_potentiel}"