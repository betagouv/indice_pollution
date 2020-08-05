from setuptools import find_packages, setup

DEPENDENCIES = [
    'flask',
    'Flask-Manage-Webpack',
    'flask-cors',
    'requests',
    'python-dateutil',
    'orjson'
]

setup(
    name='indice_pollution',
    version='0.1.2',
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

