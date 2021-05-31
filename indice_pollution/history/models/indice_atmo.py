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