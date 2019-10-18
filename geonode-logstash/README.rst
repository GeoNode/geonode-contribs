================
Geonode Logstash
================

geonode-logstash is a geonode app to send analytics metrics data to an external Logstash server.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "logstash" to your INSTALLED_APPS setting like this::

    GEONODE_CONTRIB_APPS = [
        ...
        'geonode_logstash',
    ]

3. Run `python manage.py migrate` to create the logstash models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to configure a Logstash server (you'll need the Admin app enabled).

Documentation
-------------

Learn more about this contrib app at
http://docs.geonode.org/en/master/advanced/index.html#geonode-django-contrib-apps
