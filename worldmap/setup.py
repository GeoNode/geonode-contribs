import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='geonode_worldmap',
    version='0.3',
    packages=find_packages(),
    include_package_data=True,
    license='GPL',
    description='GeoNode WorldMap applications',
    #long_description=README,
    #long_description_content_type='text/markdown',
    url='http://geonode.org',
    author='GeoNode Developers',
    author_email='dev@geonode.org',
    install_requires=[
        'datautil==0.4',
        'dicttoxml==1.7.4',
        'django-geoexplorer-worldmap==4.0.72',
        'flexidate==1.4',
        'geopy==1.22.0',
        'vectorformats==0.1',
    ],
)
