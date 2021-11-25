from indice_pollution.extensions import db
from importlib import import_module
from indice_pollution.extensions import cache

class Zone(db.Model):
    __table_args__ = {"schema": "indice_schema"}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    code = db.Column(db.String)

    @classmethod
    def get(cls, code, type_):
        return Zone.query.filter_by(code=code, type=type_).first()

    @property
    @cache.memoize(timeout=0)
    def lib(self, with_preposition=True, with_article=True):
        types = {
            "region": {"article": "la ", "preposition": "région", "module": "region", "clsname": "Region"},
            "epci": {"article": "l’", "preposition": "EPCI" , "module": "epci", "clsname": "EPCI"},
            "departement": {"article": "le ", "preposition": "département", "module": "departement", "clsname": "Departement"},
            "bassin_dair": {"article": "le ", "preposition": "bassin d’air", "module": "bassin_dair", "clsname": "BassinDAir"},
            "commune": {"article": "la ", "preposition": "commune", "module": "commune", "clsname": "Commune"},
        }
        t = types.get(self.type)
        if not t:
            return ""
        m = import_module(f"indice_pollution.history.models.{t['module']}")
        c = getattr(m, t["clsname"])
        o = db.session.query(c).filter(c.zone_id == self.id).first()
        if not o:
            return ""
        r = ""
        if with_preposition:
            if with_article:
                r = t["article"]
            r += t["preposition"] + " "
        if hasattr(o, "preposition"):
            r += o.preposition + " "
        r += o.nom
        return r


