# GeoNode Contrib Apps

## How to install it

```
pip install geonode_contribs
```

### WorldMap

For using WorldMap, first install requirements:

```
pip install -r requirements.txt
```

Then add the following applications to your INSTALLED_APPS in settings.py:

```
INSTALLED_APPS += (PROJECT_NAME,
                   'geoexplorer-worldmap',
                   'geonode_contribs.worldmap',
                   'geonode_contribs.worldmap.gazetteer',
                   'geonode_contribs.worldmap.wm_extra',
                   'geonode_contribs.worldmap.mapnotes',
                   )
```

Add the following settings in your settings file:

```
GEONODE_CLIENT_LOCATION = '/static/worldmap_client/'
USE_GAZETTEER = True
GAZETTEER_DB_ALIAS = 'default'
GAZETTEER_FULLTEXTSEARCH = False
# external services to be used by the gazetteer
GAZETTEER_SERVICES = 'worldmap,geonames,nominatim'
# this is the GeoNames key which is needed by the WorldMap Gazetteer
GAZETTEER_GEONAMES_USER = os.getenv('GEONAMES_USER', 'your-key-here')
WM_COPYRIGHT_URL = "http://gis.harvard.edu/"
WM_COPYRIGHT_TEXT = "Center for Geographic Analysis"
DEFAULT_MAP_ABSTRACT = "Your text"
# these are optionals
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'your-key-here')
USE_HYPERMAP = strtobool(os.getenv('USE_HYPERMAP', 'False'))
HYPERMAP_REGISTRY_URL = os.getenv('HYPERMAP_REGISTRY_URL', 'http://localhost:8001')
SOLR_URL = os.getenv('SOLR_URL', 'http://localhost:8983/solr/hypermap/select/')
MAPPROXY_URL = os.getenv('MAPPROXY_URL', 'http://localhost:8001')
```

Enable the WorldMap hooksets:

```
GEONODE_CLIENT_HOOKSET = 'geonode_contribs.worldmap.hooksets.WorldMapHookSet'
```

Enable the context processor in your settings.py:

```
from settings import TEMPLATES
TEMPLATES[0]['OPTIONS']['context_processors'].append('geonode_contribs.worldmap.context_processors.resource_urls')
```

In your urls.py file add the following:

```
urlpatterns = [
    url(r'', include('geonode_contribs.worldmap.wm_extra.urls',
        namespace='worldmap')),
    url(r'', include('geonode_contribs.worldmap.gazetteer.urls',
        namespace='gazetteer')),
    url(r'', include('geonode_contribs.worldmap.mapnotes.urls',
        namespace='mapnotes'))
    ] + urlpatterns
```
