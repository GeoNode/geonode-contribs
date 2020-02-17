# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2019 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from __future__ import print_function

import logging
import json
import urllib

from owslib.wfs import WebFeatureService

log = logging.getLogger(__name__)


class GeoserverDataSource(object):
    """
    Wrapper around WFS to get deserialized features for risk management app
    """
    OUTPUT_FORMATS = {'application/json': json.load}
    WFCLASS = staticmethod(WebFeatureService)

    def __init__(self, url, output_format='application/json', **kwargs):
        self.wfs = GeoserverDataSource.WFCLASS(url=url, version='2.0.0', **kwargs)
        self.output_format = output_format

    def getGETGetFeatureRequest(
        self,
        typename=None,
        filter=None,
        bbox=None,
        featureid=None,
        featureversion=None,
        propertyname=None,
        maxfeatures=None,
        storedQueryID=None,
        storedQueryParams=None,
        outputFormat=None,
        method="Get",
        startindex=None,
        sortby=None,
    ):
        """Formulate proper GetFeature request using KVP encoding
        ----------
        typename : list
            List of typenames (string)
        filter : string
            XML-encoded OGC filter expression.
        bbox : tuple
            (left, bottom, right, top) in the feature type's coordinates == (minx, miny, maxx, maxy)
        featureid : list
            List of unique feature ids (string)
        featureversion : string
            Default is most recent feature version.
        propertyname : list
            List of feature property names. '*' matches all.
        maxfeatures : int
            Maximum number of features to be returned.
        method : string
            Qualified name of the HTTP DCP method to use.
        outputFormat: string (optional)
            Requested response format of the request.
        startindex: int (optional)
            Start position to return feature set (paging in combination with maxfeatures)
        sortby: list (optional)
            List of property names whose values should be used to order
            (upon presentation) the set of feature instances that
            satify the query.
        There are 3 different modes of use
        1) typename and bbox (simple spatial query)
        2) typename and filter (==query) (more expressive)
        3) featureid (direct access to known features)
        """
        storedQueryParams = storedQueryParams or {}

        base_url = next(
            (
                m.get("url")
                for m in self.wfs.getOperationByName("GetFeature").methods
                if m.get("type").lower() == method.lower()
            )
        )
        base_url = base_url if base_url.endswith("?") else base_url + "?"

        request = {"service": "WFS", "version": self.wfs.version, "request": "GetFeature"}

        # check featureid
        if featureid:
            request["featureid"] = ",".join(featureid)
        elif bbox:
            request["bbox"] = self.wfs.getBBOXKVP(bbox, typename)
        elif filter:
            request["query"] = str(filter)
        if typename:
            typename = (
                [typename] if type(typename) == type("") else typename
            )  # noqa: E721
            if int(self.wfs.version.split(".")[0]) >= 2:
                request["typenames"] = ",".join(typename)
            else:
                request["typename"] = ",".join(typename)
        if propertyname:
            request["propertyname"] = ",".join(propertyname)
        if sortby:
            request["sortby"] = ",".join(sortby)
        if featureversion:
            request["featureversion"] = str(featureversion)
        if maxfeatures:
            if int(self.wfs.version.split(".")[0]) >= 2:
                request["count"] = str(maxfeatures)
            else:
                request["maxfeatures"] = str(maxfeatures)
        if startindex:
            request["startindex"] = str(startindex)
        if storedQueryID:
            # request["storedQuery_id"] = str(storedQueryID)
            for param in storedQueryParams:
                request[param] = storedQueryParams[param]
        if outputFormat is not None:
            request["outputFormat"] = outputFormat

        data = urllib.urlencode(request, doseq=True)

        return base_url + data

    def _patch_wfs(self):
        self.wfs.getGETGetFeatureRequest = self.getGETGetFeatureRequest

    def prepare_vparams(self, vparams, separator=":"):
        u = urllib.quote
        return [separator.join((u(k), u(str(v)),)) for k, v in vparams.items()]

    def prepare_cql_params(self, vparams, separator="="):
        u = urllib.quote
        return [separator.join((u(k), "'{}'".format(v),)) for k, v in vparams.items()]

    def get_features(self, layer_name, dim_name=None, **kwargs):
        """
        Return deserialized featurelist for given params
        @param kwargs keyword args used in viewparams
        @param dim_name optional dimension to be not null
        """
        # kwargs['dim'] = dim_name
        # vparams_list = self.prepare_vparams(kwargs)
        # vparams = {'viewparams': ';'.join(vparams_list)}
        # field_names = ['dim1', 'dim2', 'value']
        # r = self.wfs.getfeature(layer_name, propertyname=field_names, outputFormat=self.output_format, storedQueryParams=vparams, storedQueryID=1)

        """
        Using 'viewparams'
        """
        # vparams = {'viewparams': 'ra:WP6_future_proj_Hospital;ha:EQ;region:Afghanistan;adm_code:AF;d1:Hospital;d2:10'}
        # field_names = ['risk_analysis','hazard_type','admin','adm_code','region','value','dim1_value','dim2_value','dim3_value','dim4_value','dim5_value', 'value']
        # r = self.wfs.getfeature('{}'.format(layer_name), propertyname=field_names, outputFormat=self.output_format, storedQueryParams=vparams, storedQueryID=1)

        """
        Using 'cql_filter'
        """
        cql_params_list = self.prepare_cql_params(kwargs)
        if dim_name is not None:
            cql_params_list.append('{}_value is not null'.format(dim_name))
        cql_filter = {'cql_filter': " and ".join(cql_params_list)}
        # cql_filter = {'cql_filter': "(risk_analysis='WP6_future_proj_Hospital' and hazard_type='EQ' and adm_code='AF' and dim1_value='Hospital')"}
        field_names = ['risk_analysis', 'hazard_type', 'admin', 'adm_code', 'region',
                       'dim1_value', 'dim2_value', 'dim3_value', 'dim4_value', 'dim5_value',
                       'dim1_order', 'dim2_order', 'dim3_order', 'dim4_order', 'dim5_order',
                       'value']
        log.info("querying %s:%s with cql params: %s" % (layer_name, dim_name, cql_filter))
        self._patch_wfs()
        r = self.wfs.getfeature('{}_data'.format(layer_name), propertyname=field_names, outputFormat=self.output_format, storedQueryParams=cql_filter, storedQueryID='riskDataStoredQuery')

        return self.deserialize(r)

    def deserialize(self, val):
        d = self.OUTPUT_FORMATS[self.output_format]
        return d(val)
