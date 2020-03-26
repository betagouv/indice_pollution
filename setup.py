from setuptools import find_packages, setup

DEPENDENCIES = [
    'flask',
    'Flask-Manage-Webpack',
    'requests',
]

setup(
    name='indice_pollution',
    version='0.0.1',
    description='API giving pollution level in France',
    url='https://beta.gouv.fr',
    author='Vincent Lara',
    author_email='vincent.lara@beta.gouv.fr',
    license='MIT',
    classifiers=[
        'Development Status :: 4 Beta',
        'Intended Audience :: Developpers',
        'Programming Language :: Python :: 3'
    ],
    keywords='taxi transportation',
    packages=find_packages(),
    install_requires=DEPENDENCIES
)

