from indice_pollution.models import db
import json

class IndiceHistory(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    date_ = db.Column(db.Date, nullable=False)
    insee = db.Column(db.String, nullable=False)
    features = db.Column(db.JSON, nullable=False)

    @classmethod
    def get(cls, date_, insee):
        return db.session.query(cls).filter_by(date_=date_, insee=insee).first()
    
    @classmethod
    def get_bulk(cls, date_, insee_list):
        return cls.query\
            .filter(cls.date_==date_, cls.insee.in_(set(insee_list)))\
            .all()

    @classmethod
    def get_after(cls, date_, insee):
        return [v.features for v in cls.query.filter(cls.date_ >= date_, cls.insee==insee).all()]

    @classmethod
    def get_or_create(cls, date_, insee, features):
        result =  cls.get(date_, insee)
        if result:
            return result
        result = cls(date_=date_, insee=insee, features=features)
        db.session.add(result)
        return result