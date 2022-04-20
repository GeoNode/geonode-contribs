Geonode SOS Services
====================


geonode-sos is a geonode app used to harvest SOS 2 sensors into geonode services


Quick start
-----------

1. Add "geonode-sos" to your INSTALLED_APPS setting like this::

    ```python
    INSTALLED_APPS += ('geonode_sos',)
    ```

2. Add this line in `settings.py` to enable the extra type module to GeoNode
    ```python
    SERVICES_TYPE_MODULES = ["geonode_sos.sos_handler.HandlerDescriptor"]
    ```

2. Add this line in `settings.py` add the extra database router in GeoNode
    ```python
    DATABASE_ROUTERS = ["geonode_sos.router.DatastoreRouter"]
    ```
