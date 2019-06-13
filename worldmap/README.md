# WorldMap

By using the WorldMap optional application, GeoNode is extended with the following additional features:

* a customized GeoExplorer viewer
    * the table of contents is hierarchical with layer categories. When a layer is added a new category containing the layer is added to the table of contents. If the category is already in the table of contents, then the layer is added to it. By default the category is the same as the layer's topic category, but that can be renamed by right clicking on it
    * the "Add Layers" dialog comes with a "Search" tab which uses Hypermap Registry (Hypermap) as a catalogue of remote and local layers. Hypermap is a requirement when using the WorldMap contrib application
* a gazetteer application: it is possible to add a given layer to a gazetteer. The gazetteer can be checked using the map client. When a layer is part of the gazetter it is possible to include it in a general gazetteer or in a specific project one. It is possible to search place names in the gazetteer by date range, in which case it is necessary to specify the layer attributes for the start and end depict dates

## Installation

### Requirements

We are assuming a Ubuntu 16.04.1 LTS development environment, but these instructions can be adapted to any recent Linux distributions:

```
# Install Ubuntu dependencies
sudo apt-get update
sudo apt-get install python-virtualenv python-dev libxml2 libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev libpq-dev libgdal-dev git default-jdk postgresql postgis

# Install Java 8 (needed by latest GeoServer 2.14)
sudo apt install -y openjdk-8-jre openjdk-8-jdk
sudo update-java-alternatives --set java-1.8.0-openjdk-amd64
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export PATH=$JAVA_HOME'bin/java':$PATH
```

### Virtual environment creation and installation of Python packages

Create and activate the virtual environment:

    cd ~
    virtualenv --no-site-packages env
    . env/bin/activate

Now install GeoNode from source code:

    git clone -b https://github.com/geonode/geonode.git
    cd geonode
    pip install -r requirements.txt
    pip install pygdal==1.11.3.3
    pip install -e .
    paver setup
    paver sync

Install worldmap:

    pip install geonode_worldmap

Then add the following applications to your INSTALLED_APPS in settings.py:

```
INSTALLED_APPS += (PROJECT_NAME,
                   'geoexplorer-worldmap',
                   'geonode_worldmap',
                   'geonode_worldmap.gazetteer',
                   'geonode_worldmap.wm_extra',
                   'geonode_worldmap.mapnotes',
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
GEONODE_CLIENT_HOOKSET = 'geonode_worldmap.hooksets.WorldMapHookSet'
```

Enable the context processor in your settings.py:

```
from settings import TEMPLATES
TEMPLATES[0]['OPTIONS']['context_processors'].append('geonode_worldmap.context_processors.resource_urls')
```

In your urls.py file add the following:

```
urlpatterns = [
    url(r'', include('geonode_worldmap.wm_extra.urls',
        namespace='worldmap')),
    url(r'', include('geonode_worldmap.gazetteer.urls',
        namespace='gazetteer')),
    url(r'', include('geonode_worldmap.mapnotes.urls',
        namespace='mapnotes'))
    ] + urlpatterns
```

### Start the Server

Start GeoNode with Worldmap using pavement::

    python manage.py runserver 0.0.0.0:8000
    paver start_geoserver

To upload layers you can login with the default GeoNode administrative account:

user: admin
password: admin

### Configuring instance for production

Please follow best practices suggested by GeoNode documentation:

http://docs.geonode.org/en/master/tutorials/advanced/geonode_production/

Remember to add the ip of your server in ALLOWED_HOSTS in the local_settings.py file::

    ALLOWED_HOSTS = ['localhost', '128.31.22.73', ]

## Hypermap Registry

GeoNode with the WorldMap contribute module requires a Hypermap Registry (Hypermap) running instance.

You can install Hypermap by following these instructions (use the "Manual Installation" section): http://cga-harvard.github.io/Hypermap-Registry/installation.html

Note that you can bypass Java 8 installation as it was installed previously. As a search engine you should install Solr, as we haven't tested Elasticsearch with WorldMap so far. Create a specific virtual environment for Hypermap in order not to interfere with the GeoNode/WorldMap virtual environment.

After installing Hypermap, start it on a different port than 8000, for example::

    python manage.py runserver 0.0.0.0:8001

In another shell start the Celery process as well::

    cd HHypermap
    celery -A hypermap worker --beat --scheduler django -l info

## Test the stack

Now that GeoNode/WorldMap and Hypermap are both running, test the stack by uploading a layer.

Login in GeoNode (admin/admin) and upload a shapefile from this page: http://localhost:8000/layers/upload

Make sure the shapefile is correctly displayed in GeoNode by going to the layer page.

Now login in Hypermap (admin/admin) and go to the admin services page: http://localhost:8001/admin/aggregator/service/ Add a service like this:

    * Title: My GeoNode WorldMap SDI
    * Url: http://localhost:8000/
    * Type: GeoNode WorldMap

Go to the Hypermap service page and check it the service and the layer is there:
http://localhost:8001/registry/

In order to have layers in the search engine (Solr) there are two options:

1) from task runner press the "Index cached layers" button
2) schedule a task in celery

We recommend the second option, which can be configured in the next section.

## Schedule Celery tasks

Go to the Periodic Task administrative interface: http://localhost:8001/admin/django_celery_beat/periodictask/

Create the following two tasks:

### Index Cached Layer Task

This task will sync the layers from the cache to the search engine. Layers are sent in the cache every time they are saved:

    * Name: Index Cached Layer
    * Task (registered): hypermap.aggregator.tasks.index_cached_layers
    * Interval: every 1 minute (or as needed)

### Check Worldmap Service

This task will do a check of all of WorldMap service:

    * Name: Check WorldMap Service
    * Task (registered): hypermap.aggregator.tasks.check_service
    * Interval: every 1 minute (or as needed)
    * Arguments: [1] # 1 is the id of the service. Change it as is needed

Now upload a new layer in GeoNode/WorldMap and check if it appears in Hypermap and in Solr (you may need to wait for the tasks to be executed)

### Update Last GeoNode WorldMap Layers

If your GeoNode/WorldMap instance has many layers, it is preferable to runt the check_service not so often, as it can be time consuming, and rather use the update_last_wm_layers.

As a first thing, change the interval for the check_service task you created for GeoNode/WorldMap to a value such as "one day" or "one week".

Then create the following periodic task:

    * Name: Sync last layers in WorldMap Service
    * Task (registered): hypermap.aggregator.update_last_wm_layers
    * Interval: every 1 minute
    * Arguments: [1] # 1 is the id of the service. Change it as is needed
