import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='geonode_logstash',
    version='3.0',
    packages=find_packages(),
    include_package_data=True,
    license='GPL',
    description='Geonode logstash application.',
    long_description=README,
    url='http://geonode.org',
    author='GeoNode Developers',
    author_email='dev@geonode.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django :: 2.2.13',
        'Intended Audience :: Developers',
        'License :: GPL',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=[
        'six>=1.15.0',
        'python-logstash-async>=1.5.1,<2.0.0'
    ]
)
