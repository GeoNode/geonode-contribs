# WorldMap

By using the WorldMap optional application, GeoNode is extended with the following additional features:

* a customized GeoExplorer viewer
    * the table of contents is hierarchical with layer categories. When a layer is added a new category containing the layer is added to the table of contents. If the category is already in the table of contents, then the layer is added to it. By default the category is the same as the layer's topic category, but that can be renamed by right clicking on it
    * the "Add Layers" dialog comes with a "Search" tab which uses Hypermap Registry (Hypermap) as a catalogue of remote and local layers. Hypermap is a requirement when using the WorldMap contrib application
* a gazetteer application: it is possible to add a given layer to a gazetteer. The gazetteer can be checked using the map client. When a layer is part of the gazetter it is possible to include it in a general gazetteer or in a specific project one. It is possible to search place names in the gazetteer by date range, in which case it is necessary to specify the layer attributes for the start and end depict dates

## Installation

### Requirements

We are assuming a Ubuntu 16.04.1 LTS development environment, but these instructions can be adapted to any recent Linux distributions::

    # Install Ubuntu dependencies
    sudo apt-get update
    sudo apt-get install python-virtualenv python-dev libxml2 libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev libpq-dev libgdal-dev git default-jdk postgresql postgis

    # Install Java 8 (needed by latest GeoServer 2.14)
    sudo apt install -y openjdk-8-jre openjdk-8-jdk
    sudo update-java-alternatives --set java-1.8.0-openjdk-amd64
    export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
    export PATH=$JAVA_HOME'bin/java':$PATH

### Virtual environment creation and installation of Python packages

Create and activate the virtual environment::

    cd ~
    virtualenv --no-site-packages env
    . env/bin/activate

Now install GeoNode from source code::

    git clone -b https://github.com/geonode/geonode.git
    cd geonode
    pip install -r requirements.txt
    pip install pygdal==1.11.3.3
    pip install -e .
    paver setup
    paver sync

Set the following environment variables as needed (change SITE_NAME and SERVER_IP s needed. Also HYPERMAP_REGISTRY_URL and SOLR_URL may be different). Even better, create a file and source it::

      export USE_WORLDMAP=True
      export SITE_NAME=worldmap
      export SERVER_IP=128.31.22.73
      export PG_USERNAME=worldmap
      export PG_PASSWORD=worldmap
      export PG_WORLDMAP_DJANGO_DB=worldmap
      export PG_WORLDMAP_UPLOADS_DB=wmdata
      export OWNER=$PG_USERNAME
      export ALLOWED_HOSTS="localhost, $SERVER_IP, "
      export GEOSERVER_LOCATION=http://localhost:8080/geoserver/
      export GEOSERVER_PUBLIC_LOCATION=http://$SERVER_IP/gs/
      export SOLR_URL =http://localhost:8983/solr/hypermap/select/
      export HYPERMAP_REGISTRY_URL =http://localhost:8001
      export MAPPROXY_URL=http://localhost:8001


You can install GeoNode WorldMap in two different ways:

1) By installing GeoNode itself
2) By using the recommended way of a geonode-project

### GeoNode/WorldMap without a geonode-project

Add the module in the `INSTALLED_APPS` section of the settings file:

```Python
    INSTALLED_APPS = (
        ...,
        'geonode.contrib.worldmap',
        ...
    )
```

Here is a typical extract of the settings that must be used for GeoNode to use the worldmap module:

```Python
    GEONODE_CLIENT_HOOKSET = "geonode.contrib.worldmap.hooksets.WorldMapHookSet"
    CORS_ORIGIN_WHITELIST = (
        HOSTNAME
    )

    # WorldMap settings
    USE_WORLDMAP = ast.literal_eval(os.getenv('USE_WORLDMAP', 'False'))

    if USE_WORLDMAP:
        GEONODE_CLIENT_LOCATION = '/static/worldmap_client/'
        INSTALLED_APPS += (
            'geoexplorer-worldmap',
            'geonode.contrib.worldmap.gazetteer',
            'geonode.contrib.worldmap.wm_extra',
            'geonode.contrib.worldmap.mapnotes',
        )
        # WorldMap Gazetter settings
        USE_GAZETTEER = True
        GAZETTEER_DB_ALIAS = 'default'
        GAZETTEER_FULLTEXTSEARCH = False
        # external services to be used by the gazetteer
        GAZETTEER_SERVICES = 'worldmap,geonames,nominatim'
        # this is the GeoNames key which is needed by the WorldMap Gazetteer
        GAZETTEER_GEONAMES_USER = os.getenv('GEONAMES_USER', 'your-key-here')
        WM_COPYRIGHT_URL = "http://gis.harvard.edu/"
        WM_COPYRIGHT_TEXT = "Center for Geographic Analysis"
        DEFAULT_MAP_ABSTRACT = """
            <h3>The Harvard WorldMap Project</h3>
            <p>WorldMap is an open source web mapping system that is currently
            under construction. It is built to assist academic research and
            teaching as well as the general public and supports discovery,
            investigation, analysis, visualization, communication and archiving
            of multi-disciplinary, multi-source and multi-format data,
            organized spatially and temporally.</p>
        """
        # these are optionals
        USE_GOOGLE_STREET_VIEW = ast.literal_eval(os.getenv('USE_GOOGLE_STREET_VIEW', 'False'))
        GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'your-key-here')
        USE_HYPERMAP = ast.literal_eval(os.getenv('USE_HYPERMAP', 'False'))
        HYPERMAP_REGISTRY_URL = os.getenv('HYPERMAP_REGISTRY_URL', 'http://localhost:8001')
        SOLR_URL = os.getenv('SOLR_URL', 'http://localhost:8983/solr/hypermap/select/')
        MAPPROXY_URL = os.getenv('MAPPROXY_URL', 'http://localhost:8001')

        # define the urls after the settings are overridden
        if USE_GEOSERVER:
            if USE_WORLDMAP:
                LOCAL_GXP_PTYPE = 'gxp_gnsource'
            else:
                LOCAL_GXP_PTYPE = 'gxp_wmscsource'
            PUBLIC_GEOSERVER = {
                "source": {
                    "title": "GeoServer - Public Layers",
                    "attribution": "&copy; %s" % SITEURL,
                    "ptype": LOCAL_GXP_PTYPE,
                    "url": OGC_SERVER['default']['PUBLIC_LOCATION'] + "ows",
                    "restUrl": "/gs/rest"
                }
            }
            LOCAL_GEOSERVER = {
                "source": {
                    "title": "GeoServer - Private Layers",
                    "attribution": "&copy; %s" % SITEURL,
                    "ptype": LOCAL_GXP_PTYPE,
                    "url": "/gs/ows",
                    "restUrl": "/gs/rest"
                }
            }
            baselayers = MAP_BASELAYERS
            MAP_BASELAYERS = [PUBLIC_GEOSERVER]
            MAP_BASELAYERS.extend(baselayers)
```

Add the `WORLDMAP` url patterna to the `urls`

```Python
    ...

    # WorldMap
    if settings.USE_WORLDMAP:
        urlpatterns += [url(r'', include('geonode.contrib.worldmap.wm_extra.urls', namespace='worldmap'))]
        urlpatterns += [url(r'', include('geonode.contrib.worldmap.gazetteer.urls', namespace='gazetteer'))]
        urlpatterns += [url(r'', include('geonode.contrib.worldmap.mapnotes.urls', namespace='mapnotes'))]
```

Add the `USE_WORLDMAP` variable to the `context_processors`

```Python
        ...
        USE_WORLDMAP=settings.USE_WORLDMAP,
    )

    if settings.USE_WORLDMAP:
        defaults['GEONODE_CLIENT_LOCATION'] = getattr(
            settings,
            'GEONODE_CLIENT_LOCATION',
            '/static/worldmap/worldmap_client/'
        )

        defaults['USE_HYPERMAP'] = getattr(
            settings,
            'USE_HYPERMAP',
            False
        )

        # TODO disable DB_DATASTORE setting
        defaults['DB_DATASTORE'] = True

        defaults['HYPERMAP_REGISTRY_URL'] = settings.HYPERMAP_REGISTRY_URL

        defaults['MAPPROXY_URL'] = settings.HYPERMAP_REGISTRY_URL

        defaults['SOLR_URL'] = settings.SOLR_URL

        defaults['USE_GAZETTEER'] = settings.USE_GAZETTEER

        defaults['GAZETTEER_SERVICES'] = getattr(
            settings,
            'GAZETTEER_SERVICES',
            'worldmap,geonames,nominatim'
        )

        defaults['USE_GOOGLE_STREET_VIEW'] = settings.USE_GOOGLE_STREET_VIEW

        defaults['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY

        defaults['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY

        defaults['WM_COPYRIGHT_URL'] = getattr(
            settings,
            'WM_COPYRIGHT_URL',
            'http://gis.harvard.edu/'
        )

        defaults['WM_COPYRIGHT_TEXT'] = getattr(
            settings,
            'WM_COPYRIGHT_TEXT',
            'Center for Geographic Analysis'
        )

        defaults['HYPERMAP_REGISTRY_URL'] = settings.HYPERMAP_REGISTRY_URL

    return defaults
```

Add the `Gazetter` links to the Metadata Editor Panel into the `layer_detail.html` template

```HTML
    <i class="fa fa-list-alt fa-3x"></i>
    <h4>{% trans "Metadata" %}</h4>
    <a class="btn btn-default btn-block btn-xs" href="{% url "layer_metadata" resource.service_typename %}">{% trans "Wizard" %}</a>
    <a class="btn btn-default btn-block btn-xs" href="{% url "layer_metadata_advanced" resource.service_typename %}">{% trans "Advanced Edit" %}</a>
    <a class="btn btn-default btn-block btn-xs" href="{% url "layer_metadata_upload" resource.service_typename %}">{% trans "Upload Metadata" %}</a>
    {% if USE_WORLDMAP %}
      <a class="btn btn-default btn-block btn-xs" href="/layers/{{ resource.service_typename }}/searchable-fields">{% trans "Search" %}</a>
      <a class="btn btn-default btn-block btn-xs" href="/gazetteer/edit/{{ resource.service_typename }}">{% trans "Gazetteer" %}</a>
    {% endif %}
    </div>
```

Add the `Gazetter` attributes to the Metadata Editor View into the `layers/templates/layouts/panel.html` template

```HTML
    <div>
        {{ attribute_form.management_form }}
        <table class="table table-striped table-bordered table-condensed">
            <tr class="table-header">
                <th style="width:25px;background: #efefef;"></th>
                <th>{% trans "Attribute" %}</th>
                <th>{% trans "Label" %}</th>
                <th>{% trans "Description" %}</th>
                <th>{% trans "Display Order" %}</th>
                {% if USE_WORLDMAP %}
                  <th>{% trans "Visible" %}</th>
                  <th>{% trans "Searchable" %}</th>
                {% endif %}
            </tr>
            {% for form in attribute_form.forms %}
                {% if form.attribute %}
                    <tr>
                        <td style="width:25px;background: #efefef;"> <span class="grippy"></span></td>
                        <td><div style="display:none">{{form.id}}</div>{{form.attribute}}</td>
                        <td>{{form.attribute_label}}</td>
                        <td>{{form.description}}</td>
                        <td>{{form.display_order}}</td>
                        {% if USE_WORLDMAP %}
                          <td>{{form.visible}}</td>
                          <td>{{form.searchable}}</td>
                        {% endif %}
                    </tr>
                {% endif %}
            {% endfor %}
        </table>
      </div>
```

### GeoNode/WorldMap with a geonode-project

You will use a geonode-project in order to separate the customization of your instance from GeoNode.

Create your geonode project by using the WorldMap geonode-project as a template  (https://github.com/cga-harvard/geonode-project). Rename it to something meaningful (for example your web site name)::

    cd ~
    django-admin startproject $SITE_NAME --template=https://github.com/cga-harvard/geonode-project/archive/master.zip -epy,rst
    cd $SITE_NAME

Create a local_settings.py by copying the included template::

    cp $SITE_NAME/local_settings.py.sample $SITE_NAME/local_settings.py
    make build
    paver setup

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
