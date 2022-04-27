from setuptools import dist, find_packages, setup
from time import time
from pkginfo import UnpackedSDist

DEPENDENCIES = [
    'alembic',
    'celery',
    'celery[redis]',
    'flask',
    'Flask-caching',
    'flask-celery',
    'flask-cors',
    'flask-Migrate',
    'flask-SQLAlchemy',
    'requests',
    'python-dateutil',
    'orjson',
    'pytz',
    'beautifulsoup4',
    'html5lib',
    'pkginfo',
    'psycopg2',
    'unidecode',
    'sentry-sdk[flask]',
    'sqlalchemy',
    'redis',
]


dist.Distribution(dict(setup_requires='pkginfo'))
try:
    d = UnpackedSDist(__file__)
    VERSION = d.version
except ValueError:
    VERSION = f'0.41.{int(time())}'

setup(
    name='indice_pollution',
    version=VERSION,
    description='API giving air pollution level in France',
    url='https://github.com/l-vincent-l/indice_pollution',
    download_url='https://github.com/l-vincent-l/indice_pollution/archive/0.1.2.tar.gz',
    author='Vincent Lara',
    author_email='vincent.lara@beta.gouv.fr',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='air quality aasqa atmo iqa',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
)

