from indice_pollution.models import db
import json

class IndiceHistory(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    date_ = db.Column(db.Date, nullable=False)
    insee = db.Column(db.String, nullable=False)
    _features = db.Column("features", db.String, nullable=False)

    @property
    def features(self):
        return json.loads(self._features)

    @features.setter
    def features(self, value):
        self._features = json.dumps(value)

    @classmethod
    def get(cls, date_, insee):
        return cls.query.filter_by(date_=date_, insee=insee).first()

    @classmethod
    def get_after(cls, date_, insee):
        return [v.features for v in cls.query.filter(cls.date_ >= date_, cls.insee==insee).all()]

    @classmethod
    def get_or_create(cls, date_, insee):
        return  cls.get(date_, insee) or cls(date_=date_, insee=insee)