from sqlalchemy.sql.expression import and_
from indice_pollution.extensions import db
from psycopg2.extras import DateRange, DateTimeTZRange
from sqlalchemy.dialects.postgresql import DATERANGE, TSTZRANGE
from sqlalchemy.sql import func
import requests
import zipfile
from io import BytesIO
from xml.dom.minidom import parseString

from indice_pollution.history.models.departement import Departement
from indice_pollution.history.models.zone import Zone
from datetime import date, datetime, timedelta

class VigilanceMeteo(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    zone_id = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'))
    phenomene_id = db.Column(db.Integer)
    date_export = db.Column(db.DateTime)

    couleur_id = db.Column(db.Integer)
    validity = db.Column(TSTZRANGE(), nullable=False)

    to_show = db.Column(DATERANGE(), nullable=False)

    __table_args__ = (
        db.Index('vigilance_zone_phenomene_date_export_idx', zone_id, phenomene_id, date_export),
        {"schema": "indice_schema"},
    )

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
                        to_show=DateRange(debut.date(), fin.date() + timedelta(days=1))
                    )
                    db.session.add(obj)
                db.session.commit()

    @classmethod
    def get(cls, departement_code, date_=None):
        if type(date_) == datetime:
            date_ = date_.date()
        if date_ is None:
            date_ = date.today()

        departement_code = cls.get_departement_code(departement_code)
        if not departement_code:
            return []
        return db.session.query(
            cls
        ).join(
            Zone
        ).filter(
            Zone.type == 'departement',
            Zone.code == departement_code,
            cls.to_show.contains(date_)
        ).all()


    def __repr__(self) -> str:
        return f"<VigilanceMeteo zone_id={self.zone_id} phenomene_id={self.phenomene_id} date_export={self.date_export} couleur_id={self.couleur_id} validity={self.validity} to_show={self.to_show}>"