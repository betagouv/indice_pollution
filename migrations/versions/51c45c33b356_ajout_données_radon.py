"""Ajout données radon

Revision ID: 51c45c33b356
Revises: 60d538317728
Create Date: 2021-06-21 10:37:18.850467

"""
from re import subn
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
import requests
import csv

from sqlalchemy.sql.expression import bindparam, select, text
from sqlalchemy.sql.selectable import subquery


# revision identifiers, used by Alembic.
revision = '51c45c33b356'
down_revision = '60d538317728'
branch_labels = None
depends_on = None

oudated_communes = ['80608',  '79261',  '60475',  '79039',  '50206',  '11097',  '71587',  '16051',  '51651',  '22357',  '88392',  '78251',  '17392',  '76525',  '49319',  '74182',  '16314',  '49304',  '39566',  '28044',  '24079',  '79171',  '39347',  '39023',  '08152',  '22253',  '14164',  '30157',  '14551',  '55164',  '39195',  '14568',  '73002',  '50171',  '29129',  '27651',  '14688',  '25399',  '14423',  '39264',  '89174',  '67402',  '90073',  '05043',  '39303',  '50163',  '53004',  '14176',  '49366',  '50001',  '61496',  '24103',  '49207',  '39542',  '33338',  '50018',  '39135',  '76729',  '79279',  '69211',  '72116',  '46327',  '89484',  '60455',  '61161',  '76191',  '35147',  '39113',  '27344',  '85048',  '09317',  '14616',  '79292',  '14013',  '74011',  '14128',  '28115',  '02733',  '49065',  '62294',  '53241',  '73266',  '80594',  '14151',  '49141',  '44017',  '16214',  '48060',  '76127',  '41092',  '71288',  '25587',  '33092',  '73203',  '35113',  '88234',  '50427',  '49158',  '49274',  '41263',  '61154',  '41005',  '72082',  '50438',  '86278',  '79054',  '14373',  '87136',  '61477',  '79222',  '24561',  '49051',  '89109',  '23121',  '24283',  '28412',  '61299',  '86277',  '61311',  '41064',  '63078',  '62431',  '50154',  '76080',  '48133',  '49289',  '73118',  '89001',  '27058',  '50220',  '65312',  '24170',  '73163',  '53092',  '79098',  '61437',  '14433',  '50631',  '16017',  '65122',  '16376',  '69114',  '79328',  '27510',  '50524',  '31307',  '50080',  '71304',  '25319',  '73260',  '72081',  '39036',  '79260',  '79027',  '14417',  '53032',  '86188',  '28150',  '39115',  '14279',  '14750',  '38274',  '01205',  '24402',  '16386',  '24204',  '49037',  '24166',  '14387',  '22154',  '50318',  '43176',  '24475',  '50385',  '48014',  '27647',  '37209',  '35209',  '24503',  '49365',  '27581',  '31298',  '14596',  '52351',  '39243',  '50534',  '31438',  '49189',  '38025',  '39414',  '39158',  '24092',  '14350',  '39440',  '14296',  '24447',  '14662',  '38293',  '39089',  '35303',  '41170',  '17352',  '72108',  '72159',  '25123',  '01186',  '24127',  '81113',  '63133',  '49078',  '49318',  '18239',  '55030',  '27551',  '73111',  '61325',  '62210',  '38312',  '16202',  '49136',  '07256',  '17169',  '76674',  '24178',  '79004',  '39417',  '16410',  '89421',  '28093',  '73045',  '78524',  '16296',  '48180',  '50465',  '49044',  '24041',  '38534',  '74120',  '48078',  '14313',  '14081',  '74274',  '50320',  '26184',  '60096',  '14413',  '44160',  '21486',  '14600',  '27265',  '85299',  '81226',  '61004',  '24369',  '16344',  '16033',  '14757',  '08042',  '39186',  '14450',  '50325',  '52262',  '16294',  '79318',  '69101',  '79219',  '28241',  '41033',  '60080',  '38435',  '49186',  '14002',  '80532',  '74022',  '14763',  '71180',  '50140',  '28311',  '79107',  '14307',  '50354',  '71055',  '16259',  '49227',  '08072',  '14339',  '16332',  '49305',  '79247',  '46278',  '67014',  '70475',  '61231',  '49198',  '24389',  '27175',  '14235',  '49103',  '50622',  '01316',  '14208',  '85044',  '56038',  '01414',  '45267',  '25027',  '24033',  '51271',  '40048',  '79264',  '17103',  '50257',  '60038',  '14212',  '79168',  '89078',  '61019',  '14604',  '28083',  '38121',  '73287',  '61318',  '14359',  '28356',  '27600',  '46274',  '53095',  '57523',  '70497',  '72284',  '57585',  '28204',  '39562',  '79214',  '67439',  '87055',  '50100',  '53244',  '50620',  '24333',  '61471',  '85168',  '16115',  '86056',  '01097',  '86030',  '24368',  '14004',  '50581',  '37135',  '24181',  '79011',  '28165',  '01154',  '64020',  '14074',  '27402',  '30190',  '79033',  '28318',  '39148',  '14142',  '35301',  '49159',  '50623',  '21621',  '27626',  '49226',  '50605',  '60453',  '69237',  '60300',  '50611',  '69147',  '50477',  '14008',  '69251',  '49335',  '91222',  '24233',  '22038',  '14189',  '49254',  '50573',  '60694',  '27268',  '01122',  '15227',  '19183',  '86208',  '01172',  '28017',  '24530',  '87196',  '22167',  '46248',  '49175',  '39123',  '48047',  '76248',  '24431',  '14109',  '39069',  '14186',  '03318',  '14493',  '36206',  '14099',  '35011',  '50636',  '51261',  '22078',  '16391',  '69224',  '80551',  '77399',  '79330',  '14386',  '16417',  '27253',  '14294',  '24093',  '35254',  '17272',  '16274',  '35100',  '16328',  '69073',  '14217',  '19032',  '69146',  '50313',  '86146',  '14525',  '80209',  '50460',  '49088',  '72097',  '46300',  '77149',  '01059',  '16309',  '74245',  '78503',  '50057',  '69213',  '37120',  '85027',  '27452',  '46099',  '53254',  '28112',  '69223',  '39483',  '49091',  '48189',  '50014',  '54342',  '89340',  '50037',  '42291',  '49309',  '73112',  '91182',  '76607',  '14517',  '01442',  '02434',  '61009',  '24433',  '49150',  '39564',  '50583',  '69015',  '24344',  '27150',  '56138',  '46158',  '14580',  '70375',  '27648',  '85224',  '79178',  '49317',  '14544',  '80761',  '29203',  '53159',  '57432',  '35269',  '14691',  '14157',  '14158',  '72063',  '26297',  '15047',  '79075',  '50223',  '16129',  '61057',  '14376',  '14481',  '50308',  '49184',  '41015',  '50640',  '50073',  '80389',  '41082',  '61083',  '38016',  '46298',  '72240',  '53231',  '25531',  '27657',  '22247',  '42082',  '79051',  '61173',  '73167',  '49087',  '86067',  '14548',  '46285',  '79327',  '72033',  '14056',  '60690',  '48084',  '28262',  '49376',  '16247',  '05141',  '95259',  '24198',  '49047',  '61449',  '38014',  '79282',  '27523',  '50608',  '52225',  '65480',  '01144',  '50485',  '50627',  '49122',  '73127',  '77491',  '04198',  '61157',  '27297',  '05150',  '73198',  '25250',  '28250',  '35053',  '57722',  '69048',  '39395',  '79045',  '56183',  '39506',  '49062',  '14505',  '49115',  '50516',  '27274',  '49250',  '61383',  '14073',  '76078',  '14185',  '50007',  '28066',  '14581',  '24235',  '40107',  '27588',  '39484',  '89381',  '01413',  '14608',  '50333',  '14690',  '25137',  '49197',  '81301',  '51411',  '18123',  '49354',  '27642',  '21073',  '76639',  '02301',  '41272',  '14201',  '08443',  '50107',  '08079',  '79044',  '28133',  '07252',  '61403',  '24065',  '40302',  '49337',  '46067',  '79035',  '41240',  '24203',  '28376',  '61504',  '50103',  '01221',  '14382',  '50244',  '24047',  '25576',  '50187',  '50020',  '33107',  '14477',  '38367',  '14722',  '19127',  '19185',  '69210',  '14331',  '60649',  '60532',  '49156',  '12020',  '14444',  '01341',  '49073',  '24427',  '25610',  '29219',  '49234',  '53138',  '11298',  '50119',  '50449',  '35348',  '80419',  '76044',  '49144',  '25140',  '86043',  '48142',  '28002',  '41011',  '22123',  '09286',  '35341',  '08371',  '14666',  '53014',  '14702',  '22007',  '54506',  '02475',  '49187',  '41202',  '16228',  '37102',  '02344',  '07016',  '50043',  '53205',  '14703',  '74110',  '86219',  '28295',  '49001',  '27549',  '37227',  '41197',  '35293',  '79068',  '85052',  '14422',  '15044',  '48195',  '09302',  '24579',  '49233',  '29149',  '89448',  '14577',  '27491',  '28063',  '49046',  '73144',  '01218',  '46077',  '61285',  '53215',  '01091',  '49013',  '24391',  '79314',  '48122',  '49105',  '33267',  '09135',  '49108',  '14192',  '48125',  '35083',  '16149',  '01417',  '61172',  '25593',  '79199',  '73056',  '08493',  '38306',  '50248',  '14513',  '39287',  '49096',  '74268',  '46014',  '50131',  '22173',  '15099',  '08475',  '50337',  '72384',  '74204',  '15136',  '49098',  '49282',  '53065',  '79321',  '49202',  '49119',  '86060',  '61468',  '48023',  '88235',  '53207',  '44093',  '81260',  '53006',  '50404',  '28340',  '35048',  '50503',  '48101',  '41165',  '81296',  '24258',  '14671',  '73244',  '11329',  '44219',  '54341',  '49052',  '79188',  '49208',  '14729',  '14031',  '24099',  '38302',  '87173',  '61110',  '05175',  '22298',  '49363',  '85060',  '50089',  '77028',  '14462',  '44191',  '23231',  '42004',  '48154',  '48184',  '79240',  '19218',  '72203',  '14472',  '24270',  '49104',  '38125',  '22290',  '48057',  '14489',  '48183',  '49277',  '35267',  '41257',  '48120',  '05120',  '14597',  '89260',  '79211',  '17189',  '50348',  '28101',  '14268',  '50323',  '16156',  '21513',  '72117',  '86166',  '85107',  '49149',  '56016',  '33091',  '85166',  '14695',  '15035',  '27131',  '79173',  '49173',  '69185',  '49327',  '41210',  '73080',  '28224',  '28205',  '27270',  '48093',  '73143',  '05088',  '49081',  '15031',  '16004',  '14611',  '16411',  '63127',  '56059',  '87184',  '26354',  '15171',  '61131',  '23126',  '73046',  '39341',  '79006',  '61315',  '16094',  '85217',  '46331',  '72304',  '69195',  '36072',  '22100',  '49290',  '48197',  '49077',  '14219',  '49014',  '89473',  '38305',  '48164',  '14508',  '27092',  '39224',  '81241',  '48076',  '50301',  '56064',  '40009',  '35323',  '79325',  '79043',  '74217',  '15145',  '14749',  '48040',  '69222',  '14372',  '27416',  '07135',  '18222',  '69150',  '86021',  '58022',  '14416',  '50386',  '24044',  '27093',  '09028',  '80447',  '39075',  '50358',  '27607',  '22192',  '39309',  '86071',  '24249',  '80175',  '50242',  '21658',  '70345',  '34330',  '35344',  '27143',  '74093',  '50600',  '49191',  '14415',  '50125',  '39064',  '50160',  '32074',  '67560',  '49229',  '14075',  '39549',  '97127',  '97500',  '97500']


def upgrade():
    potentiel_radon = sa.Table(
        "potentiel_radon",
        sa.MetaData(),
        sa.Column("zone_id", sa.Integer),
        sa.Column("classe_potentiel", sa.Integer),
        schema="indice_schema"
    )
    commune_table = sa.Table(
        "commune",
        sa.MetaData(),
        sa.Column("zone_id", sa.Integer()),
        sa.Column("insee", sa.Integer),
        schema="indice_schema"
    )

    r = requests.get('https://static.data.gouv.fr/resources/connaitre-le-potentiel-radon-de-ma-commune/20190506-174309/radon.csv')
    decoded_content = r.content.decode('utf-8')
    lines = decoded_content.splitlines()
    reader = csv.reader(lines, delimiter=';')

    def format_insee(i):
        try:
            return f"{int(i):05}"
        except ValueError:
            return i

    def insert_potentiel(rows):
        for row in rows:
            if not row[2] or format_insee(row[2]) in oudated_communes:
                continue
            op.execute(
                insert(potentiel_radon).values(
                    {
                        "zone_id": sa.select((commune_table.c.zone_id,)).where(commune_table.c.insee==format_insee(row[2])),
                        "classe_potentiel": int(row[3])
                    }
                ).on_conflict_do_nothing()
            )

    rows = []
    next(reader)
    for row in reader:
        rows.append(row)
        if len(rows) < 100:
            continue
        insert_potentiel(rows)
        rows = []
    insert_potentiel(rows)



def downgrade():
    sa.execute('TRUNCATE TABLE indice_schema.potentiel_radon')

