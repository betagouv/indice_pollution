from indice_pollution.extensions import db
from indice_pollution.helpers import today
from indice_pollution.history.models.commune import Commune
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert as pg_insert
from ftplib import FTP
import os, logging, csv, io

@dataclass
class IndiceUv(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    zone_id: int = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'), primary_key=True)
    date: datetime.date = db.Column(db.Date, primary_key=True, nullable=False)
    uv_j0: int = db.Column(db.Integer)
    uv_j1: int = db.Column(db.Integer)
    uv_j2: int = db.Column(db.Integer)
    uv_j3: int = db.Column(db.Integer)

    @classmethod
    def save_all(cls):

        def get_ftp_content():
            if not os.getenv('FS_BUCKET_URL') or not os.getenv('FS_BUCKET_USERNAME') or not os.getenv('FS_BUCKET_PASSWORD'):
                logging.error('The following env vars are required: FS_BUCKET_URL, FS_BUCKET_USERNAME and FS_BUCKET_PASSWORD')
                return None
            try:
                ftp = FTP(os.getenv('FS_BUCKET_URL'))
                ftp.login(os.getenv('FS_BUCKET_USERNAME'), os.getenv('FS_BUCKET_PASSWORD'))
                bio = io.BytesIO()
                filename = f'{today().strftime("%Y%m%d")}'
                ftp.retrbinary(f'RETR {filename}.csv', callback=bio.write)
                b = bio.getvalue()
                decoded_content = b.decode('UTF-8')
                return decoded_content
            except Exception as e:
                logging.error(e)
                return None

        decoded_content = get_ftp_content()
        if decoded_content is None:
            return
        reader = csv.DictReader(
            decoded_content.splitlines(),
            delimiter=';'
        )
        indices = []

        def format_insee(raw_insee: str):
            if len(raw_insee) == 5 and raw_insee.isdigit():
                return raw_insee
            else:
                return None
        def format_uv(raw_uv: str): # '-999' or '' means no value
            if raw_uv.isdigit():
                uv = int(raw_uv)
                if uv < 0:
                    uv = None
            else:
                uv = None
            return uv

        # file header: insee;commune;date;UV_J0;UV_J1;UV_J2;UV_J3
        for row in reader:
            insee = format_insee(row['insee'])
            outdated_communes = []
            if insee and insee not in outdated_communes:
                departement_code = f'{insee[:2]}'
                if departement_code == '20': # Corse: 20 in file, 2A or 2B in db
                    insee_2a = insee.replace('20', '2A', 1)
                    commune = Commune.get(insee_2a)
                    if commune is None:
                        insee_2b = insee.replace('20', '2B', 1)
                        commune = Commune.get(insee_2b)
                else:
                    commune = Commune.get(insee)
                date_format = '%Y-%m-%d'
                try:
                    date = datetime.strptime(row['date'], date_format).date()
                except Exception as e:
                    logging.error(e)
                    continue
                if commune and date:
                    indices.append({
                        **{
                            "zone_id": commune.zone_id,
                            "date": date,
                            "uv_j0": format_uv(row['UV_J0']),
                            "uv_j1": format_uv(row['UV_J1']),
                            "uv_j2": format_uv(row['UV_J2']),
                            "uv_j3": format_uv(row['UV_J3'])
                        }
                    })
        ins = pg_insert(cls)\
            .values(indices)\
            .on_conflict_do_nothing()
        db.session.execute(ins)
        db.session.commit()

    @classmethod
    def get(cls, insee, date_=None):
        date_ = date_ or today()
        query = cls.query.join(Commune, Commune.zone_id == cls.zone_id).filter(Commune.insee == insee, IndiceUv.date==date_)
        return query.first()

    @property
    def label(self):
        if type(self.uv_j0) == int:
            if self.uv_j0 >= 11:
                label = 'Extrême'
            elif self.uv_j0 >= 8:
                label = 'Très\u00a0fort' # unbreakable space
            elif self.uv_j0 >= 6:
                label = 'Fort'
            elif self.uv_j0 >= 3:
                label = 'Modéré'
            elif self.uv_j0 >= 1:
                label = 'Faible'
            else:
                label = 'Nul'
            label += f' (UV\u00a0{self.uv_j0})' # unbreakable space
        else:
            label = None
        return label