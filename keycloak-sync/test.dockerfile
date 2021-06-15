FROM registry.gitlab.com/wernerraath/my_geonode:latest

COPY src /usr/src/keycloaksync

RUN cd /usr/src/keycloaksync; pip install --upgrade -e .

COPY tmp /tmp
RUN cd /tmp/ && bash add_to_django.sh