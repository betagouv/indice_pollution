from setuptools import find_packages, setup
from time import time

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



def get_version():
    VERSION = f'0.41.{int(time())}'
    from pathlib import Path
    pkg_info_file = Path('.').parent / 'PKG_INFO'
    if pkg_info_file.exists():
        for line in pkg_info_file.read_text().splitlines():
            if line.startswith("Version") and ":" in line:
                return line[line.index(":")+1:].strip()
    return VERSION

setup(
    name='indice_pollution',
    version=get_version(),
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

