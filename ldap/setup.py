import io
from os.path import (
    dirname,
    join,
)
from setuptools import (
    find_packages,
    setup
)


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf-8")
    ).read()


setup(
    name="geonode_ldap",
    version="1.0.0",
    description="GeoNode contrib app for integrating with django_auth_ldap",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Ricardo Garcia Silva",
    author_email="ricardo.garcia.silva@gmail.com",
    url="https://github.com/GeoNode/geonode-contribs",
    license="GPL",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django-auth-ldap",
        "geonode",
        "python-ldap",
    ],
)
