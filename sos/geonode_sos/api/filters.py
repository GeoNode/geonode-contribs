from rest_framework.filters import BaseFilterBackend, SearchFilter
import ast

VIEW_FILTERS = {
    "sosservice": {
        "sos_url": "base_url__icontains",
        "sensor_title": "layer__title__icontains",
        "sensor_name": "layer__name__icontains",
        "observable_property": "layer__extrametadata__metadata__definition__icontains",
    },
    "default": {
        "sos_url": "remote_service__base_url__icontains",
        "sensor_title": "title__icontains",
        "sensor_name": "name__icontains",
        "observable_property": "extrametadata__metadata__definition__icontains",
    }
}


class FOISFilter(BaseFilterBackend):
    """
    Filter the FOIS by the value inside the payload.
    Accept a dictionary where:
     - the key is the Model fiel
     - an array with the value to use for filtering
    """

    def filter_queryset(self, request, queryset, view):
        if request.data:
            _filter = {f"{key}__in": value for key, value in request.data.items()}
            return queryset.filter(**_filter)
        return queryset



class CustomSensorsFilter(SearchFilter):

    def filter_queryset(self, request, queryset, view):
        _filters = request.GET
        if not _filters:
            return queryset

        sos_url = _filters.pop("sos_url", None)
        title = _filters.pop("sensor_title", None)
        observable_property = _filters.pop("observable_property", None)
        sensor_name = _filters.pop("sensor_name", None)
        _filter = {}
        _field_filters = VIEW_FILTERS.get(view.basename, VIEW_FILTERS.get('default'))
        if sos_url:
            _filter[_field_filters.get('sos_url')] = sos_url[0]
        if title:
            _filter[_field_filters.get('sensor_title')] = title[0]
        if sensor_name:
            _filter[_field_filters.get('sensor_name')] = sensor_name[0]
        if observable_property:
            _filter[_field_filters.get('observable_property')] = observable_property[0]

        # generating the other filters dynamically
        for _key, _value in _filters.items():
            try:
                if _value.isnumeric():
                    _filter[f"{_key}"] = ast.literal_eval(_value)
                else:
                    _filter[f"{_key}__icontains"] = _value
            except Exception:
                raise
        return queryset.filter(**_filter)


