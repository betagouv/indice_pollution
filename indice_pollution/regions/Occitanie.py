from . import ForecastMixin, EpisodeMixin
import requests
import json
from bs4 import BeautifulSoup
from dateutil.parser import parse

class Service(object):
    is_active_= True
    website = 'https://www.atmo-occitanie.org/'
    nom_aasqa = 'ATMO Occitanie'
    attributes_key = 'attributes'

    insee_epci = {
        '46042': '200023737',
        '46224': '200023737',
        '46156': '200023737',
        '46137': '200023737',
        '46191': '200023737',
        '46095': '200023737',
        '46197': '200023737',
        '46007': '200023737',
        '46268': '200023737',
        '46064': '200023737',
        '46088': '200023737',
        '46322': '200023737',
        '46080': '200023737',
        '46149': '200023737',
        '46044': '200023737',
        '46070': '200023737',
        '46109': '200023737',
        '46046': '200023737',
        '46032': '200023737',
        '46211': '200023737',
        '46340': '200023737',
        '46205': '200023737',
        '46320': '200023737',
        '46188': '200023737',
        '46119': '200023737',
        '46134': '200023737',
        '46136': '200023737',
        '46040': '200023737',
        '46171': '200023737',
        '46112': '200023737',
        '46256': '200023737',
        '46264': '200023737',
        '46280': '200023737',
        '46223': '200023737',
        '46190': '200023737',
        '46037': '200023737',
        '66136': '200027183',
        '66037': '200027183',
        '66172': '200027183',
        '66180': '200027183',
        '66028': '200027183',
        '66164': '200027183',
        '66195': '200027183',
        '66021': '200027183',
        '66213': '200027183',
        '66038': '200027183',
        '66017': '200027183',
        '66189': '200027183',
        '66144': '200027183',
        '66182': '200027183',
        '66227': '200027183',
        '66212': '200027183',
        '66140': '200027183',
        '66069': '200027183',
        '66224': '200027183',
        '66012': '200027183',
        '66176': '200027183',
        '66174': '200027183',
        '66145': '200027183',
        '66186': '200027183',
        '66014': '200027183',
        '66071': '200027183',
        '66101': '200027183',
        '66138': '200027183',
        '66228': '200027183',
        '66127': '200027183',
        '66041': '200027183',
        '66205': '200027183',
        '66231': '200027183',
        '66118': '200027183',
        '66042': '200027183',
        '66030': '200027183',
        '11069': '200035715',
        '11397': '200035715',
        '11429': '200035715',
        '11279': '200035715',
        '11099': '200035715',
        '11272': '200035715',
        '11315': '200035715',
        '11425': '200035715',
        '11081': '200035715',
        '11088': '200035715',
        '11288': '200035715',
        '11009': '200035715',
        '11199': '200035715',
        '11068': '200035715',
        '11005': '200035715',
        '11018': '200035715',
        '11301': '200035715',
        '11190': '200035715',
        '11022': '200035715',
        '11286': '200035715',
        '11426': '200035715',
        '11280': '200035715',
        '11198': '200035715',
        '11433': '200035715',
        '11259': '200035715',
        '11410': '200035715',
        '11084': '200035715',
        '11404': '200035715',
        '11037': '200035715',
        '11085': '200035715',
        '11437': '200035715',
        '11293': '200035715',
        '11215': '200035715',
        '11201': '200035715',
        '11253': '200035715',
        '11023': '200035715',
        '11027': '200035715',
        '11251': '200035715',
        '11122': '200035715',
        '11220': '200035715',
        '11299': '200035715',
        '11102': '200035715',
        '11396': '200035715',
        '11001': '200035715',
        '11330': '200035715',
        '11340': '200035715',
        '11408': '200035715',
        '11151': '200035715',
        '11327': '200035715',
        '11308': '200035715',
        '11325': '200035715',
        '11011': '200035715',
        '11146': '200035715',
        '11422': '200035715',
        '11025': '200035715',
        '11095': '200035715',
        '11342': '200035715',
        '11416': '200035715',
        '11042': '200035715',
        '11043': '200035715',
        '11257': '200035715',
        '11357': '200035715',
        '11378': '200035715',
        '11056': '200035715',
        '11242': '200035715',
        '11423': '200035715',
        '11075': '200035715',
        '11200': '200035715',
        '11205': '200035715',
        '11368': '200035715',
        '11387': '200035715',
        '11179': '200035715',
        '11092': '200035715',
        '11314': '200035715',
        '11016': '200035715',
        '11248': '200035715',
        '11083': '200035715',
        '11133': '200035715',
        '11440': '200035715',
        '11227': '200035715',
        '11395': '200035715',
        '11414': '200035715',
        '11223': '200035715',
        '30007': '200066918',
        '30243': '200066918',
        '30294': '200066918',
        '30132': '200066918',
        '30284': '200066918',
        '30259': '200066918',
        '30223': '200066918',
        '30305': '200066918',
        '30010': '200066918',
        '30274': '200066918',
        '30307': '200066918',
        '30027': '200066918',
        '30042': '200066918',
        '30269': '200066918',
        '30214': '200066918',
        '30152': '200066918',
        '30077': '200066918',
        '30348': '200066918',
        '30173': '200066918',
        '30147': '200066918',
        '30270': '200066918',
        '30051': '200066918',
        '30165': '200066918',
        '30253': '200066918',
        '30142': '200066918',
        '30046': '200066918',
        '30330': '200066918',
        '30080': '200066918',
        '30130': '200066918',
        '30053': '200066918',
        '30159': '200066918',
        '30285': '200066918',
        '30100': '200066918',
        '30188': '200066918',
        '30129': '200066918',
        '30271': '200066918',
        '30268': '200066918',
        '30162': '200066918',
        '30177': '200066918',
        '30055': '200066918',
        '30101': '200066918',
        '30168': '200066918',
        '30239': '200066918',
        '30267': '200066918',
        '30298': '200066918',
        '30072': '200066918',
        '30109': '200066918',
        '30329': '200066918',
        '30158': '200066918',
        '30250': '200066918',
        '30240': '200066918',
        '30203': '200066918',
        '30345': '200066918',
        '30275': '200066918',
        '30291': '200066918',
        '30079': '200066918',
        '30090': '200066918',
        '30197': '200066918',
        '30316': '200066918',
        '30261': '200066918',
        '30318': '200066918',
        '30161': '200066918',
        '30022': '200066918',
        '30264': '200066918',
        '30320': '200066918',
        '30094': '200066918',
        '30137': '200066918',
        '30323': '200066918',
        '30335': '200066918',
        '30236': '200066918',
        '30246': '200066918',
        '30044': '200066918',
        '32013': '200066926',
        '32307': '200066926',
        '32331': '200066926',
        '32162': '200066926',
        '32083': '200066926',
        '32301': '200066926',
        '32117': '200066926',
        '32279': '200066926',
        '32312': '200066926',
        '32282': '200066926',
        '32348': '200066926',
        '32368': '200066926',
        '32076': '200066926',
        '32019': '200066926',
        '32335': '200066926',
        '32054': '200066926',
        '32204': '200066926',
        '32298': '200066926',
        '32207': '200066926',
        '32091': '200066926',
        '32382': '200066926',
        '32347': '200066926',
        '32384': '200066926',
        '32112': '200066926',
        '32183': '200066926',
        '32089': '200066926',
        '32258': '200066926',
        '32024': '200066926',
        '32059': '200066926',
        '32453': '200066926',
        '32014': '200066926',
        '32316': '200066926',
        '32251': '200066926',
        '32003': '200066926',
        '09122': '200067791',
        '09324': '200067791',
        '09332': '200067791',
        '09207': '200067791',
        '09272': '200067791',
        '09245': '200067791',
        '09264': '200067791',
        '09103': '200067791',
        '09104': '200067791',
        '09121': '200067791',
        '09130': '200067791',
        '09293': '200067791',
        '09329': '200067791',
        '09273': '200067791',
        '09066': '200067791',
        '09258': '200067791',
        '09210': '200067791',
        '09099': '200067791',
        '09236': '200067791',
        '09269': '200067791',
        '09174': '200067791',
        '09202': '200067791',
        '09173': '200067791',
        '09101': '200067791',
        '09327': '200067791',
        '09138': '200067791',
        '09284': '200067791',
        '09137': '200067791',
        '09049': '200067791',
        '09300': '200067791',
        '09044': '200067791',
        '09340': '200067791',
        '09093': '200067791',
        '09021': '200067791',
        '09234': '200067791',
        '09063': '200067791',
        '09013': '200067791',
        '09179': '200067791',
        '09256': '200067791',
        '09068': '200067791',
        '09090': '200067791',
        '09072': '200067791',
        '65440': '200069300',
        '65286': '200069300',
        '65047': '200069300',
        '65100': '200069300',
        '65417': '200069300',
        '65235': '200069300',
        '65062': '200069300',
        '65331': '200069300',
        '65433': '200069300',
        '65226': '200069300',
        '65344': '200069300',
        '65340': '200069300',
        '65251': '200069300',
        '65072': '200069300',
        '65223': '200069300',
        '65350': '200069300',
        '65395': '200069300',
        '65284': '200069300',
        '65057': '200069300',
        '65252': '200069300',
        '65366': '200069300',
        '65108': '200069300',
        '65002': '200069300',
        '65048': '200069300',
        '65313': '200069300',
        '65083': '200069300',
        '65401': '200069300',
        '65257': '200069300',
        '65080': '200069300',
        '65019': '200069300',
        '65410': '200069300',
        '65244': '200069300',
        '65070': '200069300',
        '65464': '200069300',
        '65392': '200069300',
        '65185': '200069300',
        '65005': '200069300',
        '65236': '200069300',
        '65280': '200069300',
        '65292': '200069300',
        '65271': '200069300',
        '65479': '200069300',
        '65040': '200069300',
        '65339': '200069300',
        '65422': '200069300',
        '65233': '200069300',
        '65146': '200069300',
        '65084': '200069300',
        '65065': '200069300',
        '65189': '200069300',
        '65360': '200069300',
        '65020': '200069300',
        '65406': '200069300',
        '65220': '200069300',
        '65415': '200069300',
        '65343': '200069300',
        '65281': '200069300',
        '65334': '200069300',
        '65010': '200069300',
        '65268': '200069300',
        '65201': '200069300',
        '65237': '200069300',
        '65197': '200069300',
        '65470': '200069300',
        '65321': '200069300',
        '65291': '200069300',
        '65011': '200069300',
        '65191': '200069300',
        '65067': '200069300',
        '65033': '200069300',
        '65200': '200069300',
        '65107': '200069300',
        '65247': '200069300',
        '65164': '200069300',
        '65386': '200069300',
        '65144': '200069300',
        '65052': '200069300',
        '65355': '200069300',
        '65421': '200069300',
        '65082': '200069300',
        '65345': '200069300',
        '65348': '200069300',
        '65203': '200069300',
        '65351': '200069300',
        '65038': '200069300',
        '65349': '200069300',
        '12202': '241200187',
        '12176': '241200187',
        '12133': '241200187',
        '12174': '241200187',
        '12264': '241200187',
        '12090': '241200187',
        '12146': '241200187',
        '12241': '241200187',
        '12145': '241200567',
        '12225': '241200567',
        '12084': '241200567',
        '12200': '241200567',
        '12002': '241200567',
        '12070': '241200567',
        '12178': '241200567',
        '12086': '241200567',
        '12160': '241200567',
        '12072': '241200567',
        '12204': '241200567',
        '12293': '241200567',
        '12211': '241200567',
        '48131': '241200567',
        '12180': '241200567',
        '30189': '243000643',
        '30258': '243000643',
        '30156': '243000643',
        '30155': '243000643',
        '30047': '243000643',
        '30169': '243000643',
        '30125': '243000643',
        '30082': '243000643',
        '30075': '243000643',
        '30128': '243000643',
        '30211': '243000643',
        '30060': '243000643',
        '30206': '243000643',
        '30036': '243000643',
        '30255': '243000643',
        '30356': '243000643',
        '30039': '243000643',
        '30061': '243000643',
        '30138': '243000643',
        '30257': '243000643',
        '30241': '243000643',
        '30317': '243000643',
        '30228': '243000643',
        '30281': '243000643',
        '30057': '243000643',
        '30145': '243000643',
        '30112': '243000643',
        '30249': '243000643',
        '30245': '243000643',
        '30104': '243000643',
        '30313': '243000643',
        '30122': '243000643',
        '30233': '243000643',
        '30183': '243000643',
        '30224': '243000643',
        '30180': '243000643',
        '30102': '243000643',
        '30354': '243000643',
        '30163': '243000643',
        '31555': '243100518',
        '31149': '243100518',
        '31557': '243100518',
        '31069': '243100518',
        '31157': '243100518',
        '31044': '243100518',
        '31506': '243100518',
        '31561': '243100518',
        '31488': '243100518',
        '31116': '243100518',
        '31588': '243100518',
        '31282': '243100518',
        '31417': '243100518',
        '31022': '243100518',
        '31032': '243100518',
        '31150': '243100518',
        '31056': '243100518',
        '31467': '243100518',
        '31091': '243100518',
        '31490': '243100518',
        '31445': '243100518',
        '31182': '243100518',
        '31351': '243100518',
        '31230': '243100518',
        '31389': '243100518',
        '31541': '243100518',
        '31205': '243100518',
        '31186': '243100518',
        '31088': '243100518',
        '31293': '243100518',
        '31163': '243100518',
        '31184': '243100518',
        '31355': '243100518',
        '31053': '243100518',
        '31003': '243100518',
        '31418': '243100518',
        '31352': '243100518',
        '34172': '243400017',
        '34057': '243400017',
        '34129': '243400017',
        '34123': '243400017',
        '34337': '243400017',
        '34270': '243400017',
        '34090': '243400017',
        '34198': '243400017',
        '34116': '243400017',
        '34022': '243400017',
        '34095': '243400017',
        '34202': '243400017',
        '34120': '243400017',
        '34327': '243400017',
        '34058': '243400017',
        '34088': '243400017',
        '34077': '243400017',
        '34217': '243400017',
        '34259': '243400017',
        '34169': '243400017',
        '34087': '243400017',
        '34134': '243400017',
        '34244': '243400017',
        '34307': '243400017',
        '34249': '243400017',
        '34027': '243400017',
        '34227': '243400017',
        '34179': '243400017',
        '34256': '243400017',
        '34295': '243400017',
        '34164': '243400017',
        '34032': '243400769',
        '34299': '243400769',
        '34298': '243400769',
        '34300': '243400769',
        '34324': '243400769',
        '34336': '243400769',
        '34037': '243400769',
        '34140': '243400769',
        '34166': '243400769',
        '34073': '243400769',
        '34025': '243400769',
        '34009': '243400769',
        '34084': '243400769',
        '34325': '243400769',
        '34139': '243400769',
        '34094': '243400769',
        '34085': '243400769',
        '48095': '244800405',
        '48013': '244800405',
        '48018': '244800405',
        '48137': '244800405',
        '48016': '244800405',
        '48111': '244800405',
        '48029': '244800405',
        '81065': '248100430',
        '81163': '248100430',
        '81120': '248100430',
        '81021': '248100430',
        '81209': '248100430',
        '81002': '248100430',
        '81204': '248100430',
        '81130': '248100430',
        '81238': '248100430',
        '81196': '248100430',
        '81307': '248100430',
        '81195': '248100430',
        '81034': '248100430',
        '81066': '248100430',
        '81004': '248100737',
        '81257': '248100737',
        '81144': '248100737',
        '81218': '248100737',
        '81156': '248100737',
        '81018': '248100737',
        '81052': '248100737',
        '81284': '248100737',
        '81063': '248100737',
        '81074': '248100737',
        '81097': '248100737',
        '81297': '248100737',
        '81274': '248100737',
        '81079': '248100737',
        '81059': '248100737',
        '81232': '248100737',
        '82121': '248200099',
        '82124': '248200099',
        '82025': '248200099',
        '82167': '248200099',
        '82044': '248200099',
        '82085': '248200099',
        '82052': '248200099',
        '82090': '248200099',
        '82150': '248200099',
        '82195': '248200099',
        '82001': '248200099'
    }

class Episode(Service, EpisodeMixin):
    url = 'https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/epipol_3j_occitanie/FeatureServer/0/query'

class Forecast(Service, ForecastMixin):
    url = 'https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/Indice_quotidien_de_qualit%C3%A9_de_l%E2%80%99air_pour_les_collectivit%C3%A9s_territoriales_en_Occitanie/FeatureServer/0/query'

    def params(self, date_, insee):
        zone = insee if not self.insee_epci else self.insee_epci[insee]
        return {
            'where': f"(date_ech >= CURRENT_DATE - INTERVAL '2' DAY) AND code_zone ='{zone}'",
            'outFields': "*",
            'f': 'json',
            'outSR': '4326'
        }

    IQA_TO_QUALIF = {
        "1": "tres_bon",
        "2": "bon",
        "3": "bon",
        "4": "bon",
        "5": "moyen",
        "6": "mediocre",
        "7": "mediocre",
        "8": "mediocre",
        "9": "mauvais",
        "10": "tres_mauvais"
    }

    def get_from_scraping(self, previous_results, date_, insee):
        r = requests.get(self.get_url(insee))
        soup = BeautifulSoup(r.text, 'html.parser')
        script = soup.find_all('script', {"data-drupal-selector": "drupal-settings-json"})[0]
        j = json.loads(script.contents[0])
        city_iqa = j['atmo_mesures']['city_iqa']
        occitanie_indice_dict = {
            '1': 'bon',
            '2': 'moyen',
            '3': 'degrade',
            '4': 'mauvais',
            '5': 'tres_mauvais',
            '6': 'extrement_mauvais'
        }
        return [
            self.getter({
                "indice": occitanie_indice_dict.get(v['iqa']),
                "date": str(parse(v['date']).date())
            })
            for v in city_iqa
        ]

    def get_url(self, insee):
        r = requests.get(f'https://geo.api.gouv.fr/communes/{insee}',
                params={
                    "fields": "codesPostaux",
                    "format": "json",
                    "geometry": "centre"
                }
        )
        codes_postaux = ",".join(r.json()['codesPostaux'])
        search_string = f"{r.json()['nom']} [{codes_postaux}]"
        r = requests.post(
            'https://www.atmo-occitanie.org/',
            data={
                "search_custom": search_string,
                "form_id": "city_search_block_form"
            },
            allow_redirects=False
        )
        return r.headers['Location']
