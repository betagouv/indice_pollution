from setuptools import find_packages, setup

DEPENDENCIES = [
    'alembic',
    'celery',
    'celery[redis]',
    'flask',
    'flask-celery',
    'flask-cors',
    'Flask-Manage-Webpack',
    'flask-migrate',
    'flask-sqlalchemy',
    'requests',
    'python-dateutil',
    'orjson',
    'pytz',
    'beautifulsoup4',
    'html5lib',
    'psycopg2',
    'unidecode',
    'sentry-sdk[flask]',
    'redis'
]

setup(
    name='indice_pollution',
    version='0.21.0',
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
    install_requires=DEPENDENCIES
)

