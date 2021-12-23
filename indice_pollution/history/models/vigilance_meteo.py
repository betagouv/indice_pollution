from sqlalchemy.sql.expression import and_, select
from indice_pollution.extensions import db
from psycopg2.extras import DateTimeTZRange
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.sql import func
import requests
import zipfile
from io import BytesIO
from xml.dom.minidom import parseString

from indice_pollution.history.models.departement import Departement
from indice_pollution.history.models.commune import Commune
from datetime import date, datetime, timedelta

class VigilanceMeteo(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    zone_id = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'))
    phenomene_id = db.Column(db.Integer)
    date_export = db.Column(db.DateTime)

    couleur_id = db.Column(db.Integer)
    validity = db.Column(TSTZRANGE(), nullable=False)

    __table_args__ = (
        db.Index('vigilance_zone_phenomene_date_export_idx', zone_id, phenomene_id, date_export),
        db.UniqueConstraint(zone_id, phenomene_id, date_export, validity),
        {"schema": "indice_schema"},
    )

    couleurs = {
        1: 'Vert',
        2: 'Jaune',
        3: 'Orange',
        4: 'Rouge'
    }

    phenomenes = {
        1: 'Vent',
        2: 'Pluie-Inondation',
        3: 'Orages',
        4: 'Crues',
        5: 'Neige',
        6: 'Canicule',
        7: 'Grand Froid',
        8: 'Avalanches',
        9: 'Vagues-Submersion'
    }

    @staticmethod
    def get_departement_code(code):
        if code == "20":
            return "2A"
        elif code == "120":
            return "2B"
        elif code == "175":
            return "75"
        elif code == "99":
            return None
        return code

    @classmethod
    def save_all(cls):
        def convert_datetime(a):
            return datetime.strptime(a.value, "%Y%m%d%H%M%S")
        r = requests.get("http://vigilance2019.meteofrance.com/data/vigilance.zip")
        with zipfile.ZipFile(BytesIO(r.content)) as z:
            fname = "NXFR49_LFPW_.xml"
            if not fname in z.namelist():
                return
            with z.open(fname) as f:
                x = parseString(f.read())
                date_export = convert_datetime(x.getElementsByTagName('SIV_MENHIR')[0].attributes['dateExportTU'])
                if db.session.query(func.max(cls.date_export)).first() == (date_export,):
                    return

                for phenomene in x.getElementsByTagName("PHENOMENE"):
                    departement_code = cls.get_departement_code(phenomene.attributes['departement'].value)
                    if not departement_code:
                        continue
                    departement = Departement.get(departement_code)
                    if not departement:
                        continue
                    debut = convert_datetime(phenomene.attributes['dateDebutEvtTU'])
                    fin = convert_datetime(phenomene.attributes['dateFinEvtTU'])
                    obj = cls(
                        zone_id=departement.zone_id,
                        phenomene_id=int(phenomene.attributes['phenomene'].value),
                        date_export=date_export,
                        couleur_id=int(phenomene.attributes['couleur'].value),
                        validity=DateTimeTZRange(debut, fin),
                    )
                    db.session.add(obj)
                db.session.commit()

    @classmethod
    def get_query(cls, departement_code, insee, date_):
        if not departement_code and not insee:
            return []
        if isinstance(date_, datetime):
            date_ = date_.date()
        elif date_ is None:
            date_ = date.today()

        vigilance_t = VigilanceMeteo.__table__ 
        departement_t = Departement.__table__ 

        statement = select(
            vigilance_t
        ).join(
            Departement.__table__, vigilance_t.c.zone_id == departement_t.c.zone_id
        ).filter(
            vigilance_t.c.validity.overlaps(DateTimeTZRange(date_, date_ + timedelta(hours=24)))
        ).order_by(
            vigilance_t.c.date_export.desc()
        )

        if insee:
            commune_t = Commune.__table__
            statement = statement.join(
                commune_t, departement_t.c.id == commune_t.c.departement_id
            ).filter(Commune.insee == insee)
        elif departement_code:
            statement = statement.filter(departement_t.c.code == departement_code)

        return statement.fetch(1, with_ties=True)

    @classmethod
    def get(cls, departement_code=None, insee=None, date_=None):
        orms_obj = select(cls).from_statement(cls.get_query(departement_code, insee, date_))
        return list(db.session.execute(orms_obj).scalars())

    @property
    def couleur(self) -> str:
        return self.couleurs.get(self.couleur_id)

    @property
    def phenomene(self) -> str:
        return self.phenomenes.get(self.phenomene_id)

    def __repr__(self) -> str:
        return f"<VigilanceMeteo zone_id={self.zone_id} phenomene_id={self.phenomene_id} date_export={self.date_export} couleur_id={self.couleur_id} validity={self.validity}>"

    @classmethod
    def make_max_couleur(cls, vigilances):
        couleurs = [v.couleur_id for v in vigilances]
        return max(couleurs) if couleurs else 1

    @classmethod
    def make_label(cls, vigilances, max_couleur=None):
        if not vigilances:
            return ""
        max_couleur = max_couleur or cls.make_max_couleur(vigilances)
        if max_couleur == 1:
            label = "Pas de vigilance météo"
        else:
            couleur = VigilanceMeteo.couleurs.get(max_couleur)
            if couleur:
                couleur = couleur.capitalize()
            label = f"{couleur}"
        return f"Vigilance météo: {label}"