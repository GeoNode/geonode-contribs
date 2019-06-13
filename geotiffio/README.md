# GeoTIFF IO Contrib App

TODO: Description here

## Settings

GEOTIFF_IO_ENABLED
------------------
Default: ``False``

A boolean that specifies whether the GeoTIFF.io contrib feature is enabled.  If enabled, an 'Analyze with GeoTIFF.io' button is added to the layer_detail page.

GEOTIFF_IO_BASE_URL
-------------------
Default: `https://app.geotiff.io`

A string that specifies what instance of GeoTIFF.io should be opened when the 'Analyze with GeoTIFF.io' button is clicked.

### Activation

To activate the GeoTIFF IO contrib app

1) Add the following parameters to your `settings` file:

    ```Python
    GEOTIFF_IO_ENABLED = ast.literal_eval(
        os.getenv('GEOTIFF_IO_ENABLED', 'False')
    )

    # if your public geoserver location does not use HTTPS,
    # you must set GEOTIFF_IO_BASE_URL to use http://
    # for example, http://app.geotiff.io
    GEOTIFF_IO_BASE_URL = os.getenv(
        'GEOTIFF_IO_BASE_URL', 'https://app.geotiff.io'
    )
    ```

2) Add the following lines to `geonode.layers.views` file:

    ```Python
    def layer_detail(request, layername, template='layers/layer_detail.html'):
        ...
        # maps owned by user needed to fill the "add to existing map section" in template
        if request.user.is_authenticated():

            ...

            if settings.GEOTIFF_IO_ENABLED:
                from geonode.contrib.geotiffio import create_geotiff_io_url
                context_dict["link_geotiff_io"] = create_geotiff_io_url(layer, access_token)

        return TemplateResponse(
            request, template, context=context_dict)
    ```
