from sqlalchemy.sql.elements import _corresponding_column_or_error
from indice_pollution.extensions import db
import json
from .commune import Commune
from flask import current_app

class EpisodeHistory(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    date_ = db.Column(db.Date, nullable=False)
    polluant = db.Column(db.String)
    code_zone = db.Column(db.String, nullable=False)
    features = db.Column(db.JSON, nullable=False)

    def __init__(self, features) -> None:
        try:
            super().__init__(
                date_=features['date'],
                polluant=features['code_pol'],
                code_zone=str(features['code_zone']),
                features=features
            )
        except KeyError as e:
            raise e

    @classmethod
    def get(cls, date_, code_zone=None, polluant=None):
        query = db.session.query(cls).filter_by(date_=date_)
        if code_zone:
            query = query.filter_by(code_zone=code_zone)
        if polluant:
            query = query.filter_by(polluant=polluant)
        return query.first()
    
    @classmethod
    def get_bulk(cls, date_, insee_list):
        insee_list = set(insee_list)
        insee_code_zone_list = [
            (c.insee, c.code_zone)
            for c in Commune.query.filter(Commune.insee.in_(insee_list), Commune.insee != None)
        ]
        diff = insee_list - set([c[0] for c in insee_code_zone_list])
        if len(diff) > 0:
            for insee in diff:
                if len(insee) == 5:
                    commune = Commune.get(insee)
                    if commune and commune.code_zone:
                        insee_code_zone_list.append(
                            (commune.insee, commune.code_zone)
                        )
                elif len(insee) == 2:
                    insee_code_zone_list.append((insee, insee))
        code_zone_list = [c[1] for c in insee_code_zone_list]

        return cls.query\
            .filter(cls.date_==date_, cls.code_zone.in_(set(code_zone_list)))\
            .all()

    @classmethod
    def get_after(cls, date_, insee):
        if len(insee) == 5:
            code_zone = Commune.get(insee).code_zone
        else:
            code_zone = insee
        return [v.features for v in cls.query.filter(cls.date_ >= date_, cls.code_zone==code_zone).all()]

    @classmethod
    def get_or_create(cls, date_, insee=None, code_zone=None, features=None):
        if not code_zone:
            if insee and len(insee) == 5:
                commune = Commune.get(insee)
                if not commune.code_zone and 'code_zone' in features:
                    commune.code_zone = str(features['code_zone'])
                    db.session.add(commune)
                    db.session.commit()
                code_zone = commune.code_zone
            if insee and len(insee) == 2:
                code_zone = insee
        if type(features) == dict:
            polluant = features.get("code_pol") or features.get("code_polluant")
        else:
            polluant = None
        if code_zone and polluant:
            result = cls.get(date_, code_zone=code_zone, polluant=str(polluant))
            if result:
                return result
        result = cls.get(date_, code_zone=code_zone, polluant=str(polluant))
        if result:
            return result
        try:
            result = cls(features)
        except KeyError as e:
            current_app.logger.error(f"Unable to create episode with {features}")
            current_app.logger.error(e)
            return None

        if result.date_ == date_:
            db.session.add(result)
            db.session.commit()
            return result
        return None