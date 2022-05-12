Geonode SOS Services
====================


geonode-sos is a geonode app used to harvest SOS 2 sensors into geonode services

**IMPORTANT** this module is currently targeting only GeoNode 3.3.x


Quick start
-----------

1. Add "geonode-sos" to your INSTALLED_APPS setting like this::

    ```python
        INSTALLED_APPS += ('geonode_sos', 'dynamic_models',)
    ```

2. Add this line in `settings.py` to enable the extra type module to GeoNode
    ```python
    SERVICES_TYPE_MODULES = ["geonode_sos.sos_handler.HandlerDescriptor"]
    ```

2. Add this line in `settings.py` add the extra database router in GeoNode
    ```python
    DATABASE_ROUTERS = ["geonode_sos.router.DatastoreRouter"]
    ```

1. add this dict in `settings.py` to enable dynamic models
    
    ```python
    DYNAMIC_MODELS = {
        "USE_APP_LABEL": "geonode_sos_foi"
    }
    ```

Run migrations:
    ```python
    python manage.py migrate
 
    python manage.py migrate --database=datastore
    ```
