from datetime import timedelta
from . import ForecastMixin, AttributesGetter

class Forecast(AttributesGetter, ForecastMixin):
    website = 'https://www.atmo-nouvelleaquitaine.org/'
    url = 'https://opendata.atmo-na.org/geoserver/ind_nouvelle_aquitaine_agglo/wfs'

    attributes_key = 'properties'
    use_dateutil_parser = True

    @classmethod
    def insee_list(cls):
        return ['33063', '79005', '16102', '64102', '64445', '19272', '87085',
            '24322', '40088', '17300', '16015', '79191', '87154', '86194', '19031',
            '64300', '23096'
        ]

    @classmethod
    def params(cls, date_, insee):
        filter_zone = f'<PropertyIsEqualTo><PropertyName>code_zone</PropertyName><Literal>{insee}</Literal></PropertyIsEqualTo>'
        filter_date = f'<PropertyIsGreaterThanOrEqualTo><PropertyName>date_ech</PropertyName><Function name="dateParse"><Literal>yyyy-MM-dd</Literal><Literal>{date_}</Literal></Function></PropertyIsGreaterThanOrEqualTo>'

        return {
            'request': 'GetFeature',
            'service': 'WFS',
            'version': '1.1',
            'typeName': 'ind_nouvelle_aquitaine_agglo:ind_nouvelle_aquitaine_agglo',
            'Filter': f"<Filter><And>{filter_zone}{filter_date}</And></Filter>",
            'outputFormat': 'json',
        }