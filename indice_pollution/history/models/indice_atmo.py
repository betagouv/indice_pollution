from indice_pollution.models import db

class IndiceATMO(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    zone_id = db.Column(db.Integer, db.ForeignKey('indice_schema.zone.id'), primary_key=True)
    date_ech = db.Column(db.DateTime, primary_key=True)
    date_dif = db.Column(db.DateTime, primary_key=True)
    no2 = db.Column(db.Integer)
    so2 = db.Column(db.Integer)
    o3 = db.Column(db.Integer)
    pm10 = db.Column(db.Integer)
    pm25 = db.Column(db.Integer)
    libelle = db.Column(db.String)
