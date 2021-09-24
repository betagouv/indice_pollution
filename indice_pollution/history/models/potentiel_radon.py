from indice_pollution.extensions import db
from indice_pollution.history.models.commune import Commune
from dataclasses import dataclass

@dataclass
class PotentielRadon(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    zone_id: int = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'), primary_key=True)
    classe_potentiel: int = db.Column(db.Integer)

    @classmethod
    def get(cls, insee):
        return cls.query.join(Commune, Commune.zone_id == cls.zone_id).filter(Commune.insee == insee).first()

    @property
    def label(self):
        return {
            1: "Faible",
            2: "Moyen",
            3: "Élevé"
        }.get(self.classe_potentiel)