Geonode SOS Services
====================


geonode-sos is a geonode app used to harvest SOS sensors into geonode services


Quick start
-----------

1. Add "geonode-sos" to your INSTALLED_APPS setting like this::

    ```python
    if 'geonode_sos' not in INSTALLED_APPS:
        INSTALLED_APPS = ('geonode_sos',) + INSTALLED_APPS
    ```

2. Add this line in `settings.py` to enable the extra type module to GeoNode
    ```python
    SERVICES_TYPE_MODULES = ["geonode_sos.sos_handler.HandlerDescriptor"]
    ```
Additional Info
---------------

Main SOS parsing functionalities use [sos4py](https://github.com/52North/sos4py) library, the extra metadata are parsed with an internal parsing provided bt the SOS Handler
