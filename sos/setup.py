from setuptools import find_packages, setup

import geonode_sos


def read_file(path: str):
    with open(path, "r") as file:
        return file.read()


setup_requires = [
    "wheel",
]

setup(
    name="geonode_sos",
    version=geonode_sos.__version__,
    url=geonode_sos.__url__,
    description=geonode_sos.__doc__,
    long_description=read_file("README.md"),
    author=geonode_sos.__author__,
    author_email=geonode_sos.__email__,
    license=geonode_sos.__license__,
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django :: 3.0",
        "License :: OSI Approved :: GNU General Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(),
    package_data={"": ["*.html", "*.js"]},
    include_package_data=True,
    install_requires=["sos4py==0.3.0"],    
)
