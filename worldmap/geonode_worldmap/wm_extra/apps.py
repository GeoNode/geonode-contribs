from django.apps import AppConfig


class WMExtraConfig(AppConfig):
    name = 'geonode_worldmap.wm_extra'
    verbose_name = 'WM Extras'

    def ready(self):
        from geonode_worldmap.wm_extra import signals  # noqa
