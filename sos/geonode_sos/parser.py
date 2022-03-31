from typing import List, Optional
from owslib.etree import etree
from owslib.namespaces import Namespaces
import requests
import json


class SOSParsingException(Exception):
    pass


def get_namespaces():
    n = Namespaces()
    ns = n.get_namespaces(["ogc", "om20", "gml32", "sa", "sml", "swes", "xlink"])
    ns["gco"] = n.get_namespace("gco")
    ns["gmd"] = n.get_namespace("gmd")
    ns["ows"] = n.get_namespace("ows110")
    ns["sos"] = n.get_namespace("sos20")
    ns["swe"] = n.get_namespace("swe20")
    ns["sml"] = "http://www.opengis.net/sensorml/2.0"
    ns["gml"] = n.get_namespace("gml32")
    return ns


namespaces = get_namespaces()


class DescribeSensorParser:
    """
    Parser to extract information from the DescribeSensor request of a SOS sensor
    input -> xml_content coming from the request
    """

    def __init__(
        self, xml_content: str, sos_service: str = None, procedure_id: str = None
    ) -> None:
        self.gda = etree.fromstring(xml_content)
        self.sos_service = sos_service
        self.procedure_id = procedure_id

    def get_id(self) -> str:
        identifiers_paths = [".//gml:identifier[@codeSpace='uniqueID']"]
        return self._extract_value(self.gda, identifiers_paths)

    def get_short_name(self) -> str:
        title_paths = [".//gml:name"]
        return self._extract_value(self.gda, title_paths)

    def get_long_name(self) -> str:
        long_name_paths = [
            ".//gml:description",
        ]
        return self._extract_value(self.gda, long_name_paths)

    def get_offerings(self) -> Optional[List[dict]]:
        offerings = self.gda.findall(
            ".//sml:capabilities[@name='offerings']/sml:CapabilityList//sml:capability",
            namespaces=namespaces,
        )
        return [
            {
                "name": x.attrib.get("name"),
                "definition": x.find("swe:Text", namespaces=namespaces).attrib.get(
                    "definition"
                ),
                "value": x.find("*//swe:value", namespaces=namespaces).text,
            }
            for x in offerings
        ]

    def get_feature_of_interest(self) -> Optional[List[dict]]:
        payload = json.dumps(
            {
                "request": "GetFeatureOfInterest",
                "service": "SOS",
                "version": "2.0.0",
                "procedure": f"{self.procedure_id}",
            }
        )
        headers = {"Content-Type": "application/json"}

        feature_of_interest = (
            requests.request("POST", self.sos_service, headers=headers, data=payload)
            .json()
            .get("featureOfInterest", [])
        )

        return [
            {
                "name": item.get("name").get("value"),
                "definition": item.get("name").get("codespace"),
                "value": item.get("sampledFeature"),
            }
            for item in feature_of_interest
        ]

    def get_extra_metadata(self) -> str:
        extra = []
        for output in self.gda.iterfind(
            ".//sml:OutputList/sml:output", namespaces=namespaces
        ):
            if output.find(".//swe:Quantity", namespaces=namespaces) is not None:
                extra.append(
                    {
                        "filter_header": "Sensor Parameters",
                        "field_name": "output_name",
                        "field_label": output.attrib.get("name").lower(),
                        "field_value": output.attrib.get("name").lower(),
                    }
                )
        return extra

    def _extract_value(self, starting_path, search_path):
        for _id_path in search_path:
            _id = starting_path.find(_id_path, namespaces=namespaces)
            if _id is not None:
                return _id.text

        raise SOSParsingException(
            "No value found in path with the available identifiers path"
        )
