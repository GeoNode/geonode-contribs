import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='geonode_contribs',
    version='2.10.0',
    packages=find_packages(),
    include_package_data=True,
    license='GPL',
    description='GeoNode contrib applications',
    long_description=README,
    url='http://geonode.org',
    author='GeoNode Developers',
    author_email='dev@geonode.org'
)
