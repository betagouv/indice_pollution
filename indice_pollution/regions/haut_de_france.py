from . import ForecastMixin
from datetime import timedelta
from dateutil.parser import parse

class Forecast(ForecastMixin):
    date_format = '%Y-%m-%dT00:00:00.000Z'
    url = 'https://opendata.arcgis.com/datasets/411398950a544bcbbcdd4ef12ef07a1b_0.geojson'
    insee_list = ['59350', '59183', '59178', '62041', '62160', '59606', '02691',
        '60175', '62765', '62193', '59392', '80021', '62119']

    @classmethod
    def params(cls, date, epci=None, insee=None):
        if epci:
            raise ValueError()

        parsed_date = parse(date)
        str_parsed_date = parsed_date.strftime(cls.date_format)
        str_parsed_date = parsed_date.timestamp()
        day_after = (parsed_date + timedelta(hours=24)).strftime(cls.date_format)
        day_after = (parsed_date + timedelta(hours=24)).timestamp()
        return {
            'outFields': 'date_ech, valeur',
            'where': f"(code_zone={insee}) AND ((date_ech={str_parsed_date}) OR (date_ech={day_after}))",
            'outSR': 4326,
            'f': 'json'
        }

    @classmethod
    def getter(cls, feature):
        dt = parse(feature['attributes']['date_ech']).strftime(cls.date_format)
        return {
            'indice': feature['attributes']['valeur'],
            'date': dt.date()
        }