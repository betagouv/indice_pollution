from dataclasses import dataclass
from indice_pollution.extensions import db
from psycopg2.extras import DateRange
from sqlalchemy.dialects.postgresql import DATERANGE
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from datetime import date, datetime, timedelta
import os, requests, logging, csv, copy
from indice_pollution.history.models.commune import Commune

from indice_pollution.history.models.departement import Departement

@dataclass
class RAEP(db.Model):
    __tablename__ = "raep"

    id: int = db.Column(db.Integer, primary_key=True)
    zone_id: int = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'), nullable=False)
    validity = db.Column(DATERANGE(), nullable=False)

    cypres: int = db.Column(db.Integer)
    noisetier: int = db.Column(db.Integer)
    aulne: int = db.Column(db.Integer)
    peuplier: int = db.Column(db.Integer)
    saule: int = db.Column(db.Integer)
    frene: int = db.Column(db.Integer)
    charme: int = db.Column(db.Integer)
    bouleau: int = db.Column(db.Integer)
    platane: int = db.Column(db.Integer)
    chene: int = db.Column(db.Integer)
    olivier: int = db.Column(db.Integer)
    tilleul: int = db.Column(db.Integer)
    chataignier: int = db.Column(db.Integer)
    rumex: int = db.Column(db.Integer)
    graminees: int = db.Column(db.Integer)
    plantain: int = db.Column(db.Integer)
    urticacees: int = db.Column(db.Integer)
    armoises: int = db.Column(db.Integer)
    ambroisies: int = db.Column(db.Integer)
    total: int = db.Column(db.Integer)

    __table_args__ = (
        db.Index('raep_zone_validity_idx', zone_id, validity),
        db.UniqueConstraint(zone_id, validity),
        {"schema": "indice_schema"},
    )
    liste_allergenes = ["cypres", "noisetier", "aulne", "peuplier", "saule", "frene", "charme", "bouleau", "platane", "chene", "olivier", "tilleul", "chataignier", "rumex", "graminees", "plantain", "urticacees", "armoises", "ambroisies"]

    @classmethod
    def save_all(cls):
        if not os.getenv('ALLERGIES_URL'):
            return {}
        try:
            r = requests.get(os.getenv("ALLERGIES_URL"))
        except Exception as e:
            logging.error(e)
            return {}
        decoded_content = r.content.decode('utf-8')
        first_column_name = decoded_content[:10] #Il s'agit de la date
        date_format = "%d/%m/%Y"
        debut_validite = datetime.strptime(first_column_name, date_format).date()
        fin_validite = debut_validite + timedelta(weeks=1)
        reader = csv.DictReader(
            decoded_content.splitlines(),
            delimiter=';'
        )

        risques = []
        for r in reader:
            departement_code = f"{r[first_column_name]:0>2}"
            if departement_code == "20":
                departement_code = "2A"   
            departement = Departement.get(departement_code)
            risques.append({
                **{
                    "zone_id": departement.zone_id,
                    "total": r["Total"],
                    "validity": DateRange(debut_validite, fin_validite)
                },
                **{allergene: int(r[allergene]) for allergene in cls.liste_allergenes}
            })
            if departement_code == "2A":
                departement = Departement.get("2B")
                r = copy.deepcopy(risques[-1])
                r["zone_id"] = Departement.get("2B").zone_id
                risques.append(r)
        ins = pg_insert(cls)\
            .values(risques)\
            .on_conflict_do_nothing()
        db.session.execute(ins)
        db.session.commit()

    @classmethod
    def get(cls, insee=None, zone_id=None, date_=None):
        date_ = date_ or date.today()
        if insee:
            if len(insee) == 5:
                zone_id = Commune.get(insee).departement.zone_id
            elif len(insee) == 2:
                zone_id = Departement.get(insee).zone_id
            else:
                return None
        elif zone_id is None:
            return None
        return cls.query.filter(
            cls.zone_id == zone_id,
            cls.validity.contains(date_)
        ).order_by(
            func.upper(cls.validity).desc()
        ).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter(
            cls.validity.contains(date.today())
        ).distinct(cls.zone_id
        ).order_by(
            cls.zone_id,
            func.upper(cls.validity).desc()
        ).all()

    def to_dict(self):
        date_format = "%d/%m/%Y"
        return {
            "total": self.total,
            "allergenes": {
                allergene: getattr(self, allergene)
                for allergene in self.liste_allergenes
            },
            "periode_validite": {
                "debut": self.validity.lower.strftime(date_format),
                "fin": self.validity.upper.strftime(date_format)
            }
        }