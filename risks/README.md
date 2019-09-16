# geonode-risk_management_tools
The ``geonode-risk_management_tools`` contrib app is a GeoNode Extension built by WorldBanck GFDRR which adds the capability of extracting and managing Hazard Risks on geographical areas.

## Overview
The World Bank and GFDRR are leading an ongoing Technical Assistance (TA) to the Government of Afghanistan on Disaster Risk Management. As part of this TA, a multi-hazard risk assessment was conducted. An international consortium was hired to produce new information on hazard, exposure, vulnerability and risk, for flooding, earthquake, landslide, avalanche, and drought. Hazard and loss for different return periods was computed for all districts and regions. In addition, a cost-benefit analysis was conducted for a select number of risk reduction options for floods and earthquakes (e.g. flood levees; earthquake-proofing of buildings).

A GeoNode (http://disasterrisk.af.geonode.org/) was developed by ENEA to host and share the data. Many of the data layers have been uploaded and stylized on this GeoNode. The GeoNode is currently following the standard format. World Bank has an interest in improving the decision-making and data-extraction capabilities by expanding this GeoNode with two modules. One module should allow the user to dynamically explore the potential costs and benefits of the pre-calculated risk management options, by sliding bars, changing numbers and getting outputs in graphs, charts and a simple map. The second module should allow the user to easily extract maps and tabular results for their area and indicator of interest, again using drop-down menus and boxes that filter existing information and maps.

### Module 1: Cost-benefit Analysis & Decision Tool
This module should allow the user to use an interactive user interface (drop-down menus; slide bars; buttons) to access pre-processed tables and maps related to cost-benefit analysis of risk management options.

### Module 2: Risk Data Extraction and Visualization
This module should enable the user to easily show and extract data for the area (district, province, national) of interest. Based on the user's selection of area (linked to admin 1 and admin 2 shapefiles), indicator (linked to table and/or map), and indicator property (linked to rows and columns in the table), the user should get the correct map and a chart/graph.

# Settings

## Activation

In the ``settings.py``(or local-settings) file, enable the ``geonode_risks`` app.  

```Python
    GEONODE_CONTRIB_APPS = (
        'geonode_risks'
    )
```

## URLs

Configure the urls whithin your Django app.

```from django.conf.urls import url
from django.views.generic import TemplateView

from geonode.urls import *

urlpatterns += [
    url(r'^geonode_risks/', include('geonode_risks.urls', namespace='risks')),
]

urlpatterns = [
   url(r'^/?$',
       TemplateView.as_view(template_name='site_index.html'),
       name='home'),
] + urlpatterns
```

## Migrate

This step is needed in order to update the DB model.

```Python
    python manage.py makemigrations
    python manage.py migrate
```

## Collect static files

This step is needed in order to copy in the static dir the ``.xsl`` file that will be referenced by the
exported metadata file, and one ``.css`` file that is referenced within the xsl file.

```Python
    python manage.py collectstatic
```

This means that any customization to the output format should be performed on these files.

## Add GeoNode Top-bar Menu Links to the Risks Applications

Edit the the `site_base.html` by adding the menu options:

```HTML
 <div id="navbar" class="navbar-collapse collapse">
      <ul class="nav navbar-nav toolbar">
        {% block tabs %}
          ...
          <li id="nav_risks">
            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{% trans 'Risk Management Tools' %}<i class="fa fa-angle-down fa-lg"></i></a>
              <ul class="dropdown-menu">
                  <li><a href="{% url 'risks:cost_benefit_analysis:index' %}">{% trans "Cost/Benefit Analysis & Decision Tool" %}</a></li>
                  <li><a href="{% url 'risks:data_extraction:index' %}">{% trans "Risk Data Extraction & Visualization" %}</a></li>
              </ul>
          </li>
          ...
          {% endblock %}
        </ul>
 </div>
```

## Configure the `Risks Apps`

From the `admin dashboard` configure the two applications, by adding them if not already present.

```Python
  Home › Geonode_Risks › Risk apps

  * Cost Benefit Analysis
  * Data Extraction
```

Make sure the administrative levels have been correctly populated from `Home › Geonode_Risks › Regions`.

You can initialize them by running the management command:

```Python
    python manage.py populateau
```

## Import and convert Risk Analysis Datasets

This can be done both through the `management commands` or, more easily, through the `admin dashboards`

The section `Home › Geonode_Risks` will allow you to run:

* `Risks Analysis: Create new through a .ini descriptor file`
* `Risks Analysis: Import Risk Data from XLSX file`
* `Risks Analysis: Import or Update Risk Metadata from XLSX file`

The file format must be correct. You can find some examples inside the `geonode_risks/tests` folder.