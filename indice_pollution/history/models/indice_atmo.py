from indice_pollution.models import db
from indice_pollution.helpers import today
from indice_pollution.history.models import Commune, EPCI
from sqlalchemy import  Date
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module

@dataclass
class IndiceATMO(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    zone_id: int = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'), primary_key=True)
    date_ech: datetime = db.Column(db.DateTime, primary_key=True)
    date_dif: datetime = db.Column(db.DateTime, primary_key=True)
    no2: int = db.Column(db.Integer)
    so2: int = db.Column(db.Integer)
    o3:int = db.Column(db.Integer)
    pm10: int = db.Column(db.Integer)
    pm25: int = db.Column(db.Integer)
    valeur: int = db.Column(db.Integer)

    @classmethod
    def get(cls, insee=None, code_epci=None, date_=None):
        zone_subquery = cls.zone_subquery(insee=insee, code_epci=code_epci).subquery()
        zone_subquery_or = cls.zone_subquery_or(insee=insee).subquery()
        date_ = date_ or today()
        query = IndiceATMO\
            .query.filter(
                IndiceATMO.date_ech.cast(Date)==date_,
                ((IndiceATMO.zone_id==zone_subquery)|
                (IndiceATMO.zone_id==zone_subquery_or)
                )
            )\
            .order_by(IndiceATMO.date_dif.desc())
        return query.first()

    @classmethod
    def zone_subquery(cls, insee=None, code_epci=None):
        if insee:
            return Commune.get_query(insee=insee).with_entities(Commune.zone_id)
        elif code_epci:
            return EPCI.get_query(code=code_epci).with_entities(EPCI.zone_id)

    @classmethod
    def zone_subquery_or(cls, insee=None, code_epci=None):
        if insee:
            return EPCI.get_query(insee=insee).with_entities(EPCI.zone_id)
        elif code_epci:
            return Commune.get_query(code=code_epci).with_entities(Commune.zone_id)

    @classmethod
    def couleur_from_valeur(cls, valeur):
        return {
            "bon": "#50F0E6",
            "moyen": "#50CCAA",
            "degrade" :"#F0E641",
            "mauvais": "#FF5050",
            "tres_mauvais": "#960032",
            "extrement_mauvais": "#960032",
        }.get(cls.indice_from_valeur(valeur))

    @classmethod
    def label_from_valeur(cls, valeur):
        return {
            "bon": "Bon",
            "moyen": "Moyen",
            "degrade": "Dégradé",
            "mauvais": "Mauvais",
            "tres_mauvais": "Très mauvais",
            "extrement_mauvais": "Extrêment mauvais",
        }.get(cls.indice_from_valeur(valeur))

    @classmethod
    def indice_from_valeur(cls, valeur):
        return [
            "bon",
            "moyen",
            "degrade",
            "mauvais",
            "tres_mauvais",
            "extrement_mauvais",
        ][valeur - 1]

    @classmethod
    def indice_dict(cls, valeur):
        return {
            'indice': cls.indice_from_valeur(valeur),
            'label': cls.label_from_valeur(valeur),
            'couleur': cls.couleur_from_valeur(valeur),
        }

    @classmethod
    def sous_indice_dict(cls, code, valeur):
        return {
            **{'polluant_name': code.upper()},
            **cls.indice_dict(valeur)
        }

    def dict(self):
        return {
            **{
                'sous_indices': [self.sous_indice_dict(k, getattr(self, k)) for k in ['no2', 'so2', 'o3', 'pm10', 'pm25']],
                'date': self.date_ech.date().isoformat(),
                'valeur': self.valeur
            },
            **self.indice_dict(self.valeur)
        }