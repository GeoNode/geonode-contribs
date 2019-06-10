# GeoNode Contrib Apps

## How to install it

```
pip install geonode_contribs
```

### WorldMap

For using WorldMap contrib app add this to your INSTALLED_APPS in settings.py:

```
INSTALLED_APPS += ('geonode_contribs.worldmap')
```

Then enable the WorldMap hooksets:

```
GEONODE_CLIENT_HOOKSET = 'geonode_contribs.worldmap.hooksets.WorldMapHookSet'
```
