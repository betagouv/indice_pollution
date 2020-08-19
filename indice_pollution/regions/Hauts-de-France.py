from . import ForecastMixin
from datetime import datetime, timedelta
from dateutil.parser import parse

class Forecast(ForecastMixin):
    date_format = '%Y-%m-%d'
    website = 'https://www.atmo-hdf.fr/'
    url = 'https://services8.arcgis.com/rxZzohbySMKHTNcy/arcgis/rest/services/ind_hdf_agglo/FeatureServer/0/query'

    @classmethod
    def insee_list(cls):
        return ['59350', '59183', '59178', '62041', '62160', '59606', '02691',
        '60175', '62765', '62193', '59392', '80021', '62119']

    @classmethod
    def params(cls, date_, insee):
        parsed_date = parse(date_)
        str_parsed_date = parsed_date.strftime(cls.date_format)
        str_parsed_date = parsed_date.timestamp()
        day_after = (parsed_date + timedelta(hours=24)).strftime(cls.date_format)
        day_after = (parsed_date + timedelta(hours=24)).timestamp()
        return {
            'outFields': ",".join(cls.outfields),
            'where': f"(date_ech>= '{date_}') AND code_zone={insee}",
            'outSR': 4326,
            'f': 'json'
        }

    @classmethod
    def getter(cls, feature):
        attributes = feature['attributes']
        dt = datetime.fromtimestamp(attributes['date_ech']/1000).strftime(cls.date_format)
        return {
            **{
                'indice': feature['attributes']['valeur'],
                'date': dt
            },
            **{k: feature['attributes'][k] for k in cls.outfields if k in feature['attributes']}
        }