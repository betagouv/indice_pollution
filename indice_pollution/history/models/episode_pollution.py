from sqlalchemy.orm import relationship
from indice_pollution.history.models.commune import Commune
from indice_pollution.models import db
from datetime import datetime
from indice_pollution.helpers import today
from sqlalchemy import  Date

class EpisodePollution(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    zone_id: int = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'), primary_key=True)
    zone = relationship("indice_pollution.history.models.zone.Zone")
    date_ech: datetime = db.Column(db.DateTime, primary_key=True)
    date_dif: datetime = db.Column(db.DateTime, primary_key=True)
    code_pol: int = db.Column(db.Integer, primary_key=True)
    etat: str = db.Column(db.String)
    com_court: str = db.Column(db.String)
    com_long: str = db.Column(db.String)

    @classmethod
    def get(cls, insee=None, code_epci=None, date_=None):
        if insee:
            zone_subquery = Commune.get_query(insee=insee).with_entities(Commune.zone_pollution_id)
        date_ = date_ or today()
        query = \
            cls.query.filter(
                cls.date_ech.cast(Date)==date_,
                cls.zone_id==zone_subquery
            )\
            .order_by(cls.date_dif.desc())
        return query.all()

    @property
    def lib_pol(self):
        return {
            1: 'Dioxyde de soufre',
            3: 'Dioxyde d’azote',
            4: 'Monoxyde de carbone',
            5: 'Particules PM 10',
            7: 'Ozone',
            8: 'Dioxyde d’azote',
            24: 'Particules PM10',
            39: 'Particules PM25',
        }.get(self.code_pol)

    def dict(self):
        return {
            "code_pol": f"{self.code_pol:02}",
            "code_zone": self.zone.code,
            "com_court": self.com_court,
            "com_long": self.com_long,
            "date": self.date_ech.date().isoformat(),
            "date_ech": self.date_ech.date().isoformat(),
            "date_dif": self.date_dif.date().isoformat(),
            "etat": self.etat,
            "lib_pol": self.lib_pol
        }

