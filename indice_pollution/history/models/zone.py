from indice_pollution.extensions import db

class Zone(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    code = db.Column(db.String)


    @classmethod
    def get(cls, code, type_):
        return Zone.query.filter_by(code=code, type=type_).first()
