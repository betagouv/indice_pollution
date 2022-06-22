import pytest
import os
from requests import put
import sqlalchemy as sa
from indice_pollution import create_app
from indice_pollution.history.models import Commune, Departement, Region, Zone

# Retrieve a database connection string from the shell environment
try:
    DB_CONN = os.environ['TEST_DATABASE_URL']
except KeyError:
    raise KeyError('TEST_DATABASE_URL not found. You must export a database ' +
                   'connection string to the environmental variable ' +
                   'TEST_DATABASE_URL in order to run tests.')
else:
    DB_OPTS = sa.engine.url.make_url(DB_CONN).translate_connect_args()

pytest_plugins = ['pytest-flask-sqlalchemy']

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def app(request):
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN
    with app.app_context():
        db = app.extensions['sqlalchemy'].db
        db.engine.execute('DROP TABLE IF EXISTS alembic_version;')
        db.engine.execute('CREATE SCHEMA IF NOT EXISTS indice_schema')
        db.metadata.bind = db.engine
        db.metadata.create_all()
        yield app
        db.metadata.drop_all()


@pytest.fixture(scope='function')
def _db(app):
    db = app.extensions['sqlalchemy'].db
    tables = ','.join([f'{table.schema}."{table.name}"'
                 for table in reversed(db.metadata.sorted_tables)])
    sql = f'TRUNCATE {tables} RESTART IDENTITY;'
    db.session.execute(sql)
    db.session.commit()
    return db

@pytest.fixture(scope='function')
def commune(db_session) -> Commune:
    region = Region(nom="Pays de la Loire", code="52")
    zone_departement = Zone(type='departement', code='53')
    departement = Departement(nom="Mayenne", code="53", region=region, zone=zone_departement)
    zone = Zone(type='commune', code='53130')
    commune = Commune(nom="Laval", code="53130", codes_postaux=["53000"], zone=zone, zone_pollution=departement.zone, departement=departement)
    db_session.add_all([region, zone_departement, departement, zone, commune])
    return commune

@pytest.fixture(scope='function')
def commune_commited(commune, db_session) -> Commune:
    db_session.commit()
    return commune
