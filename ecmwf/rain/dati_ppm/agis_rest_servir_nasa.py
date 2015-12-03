__author__ = 'fabio.lana'
# from arcgis import ArcGIS



# FUNZIONA CON I VETTORI
# source1 = "http://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Congressional_Districts/FeatureServer"
# service1 = ArcGIS(source1)
# layer_id = 0
# campi = service1.enumerate_layer_fields(0)
# for campo in campi:
#     print campo
# shapes = service1.get(layer_id, "STATE_ABBR='IN'")
# FUNZIONA CON I VETTORI

from owslib.wms import WebMapService

# wms_tutti = WebMapService('http://ags.servirlabs.net/arcgis/services/Global/MapServer/WMSServer?', version='1.1.1')
# wms_tutti.getcapabilities()

wms_imerg = WebMapService('http://ags.servirlabs.net/arcgis/services/Global/IMERG_30Min/MapServer/WMSServer?request=GetCapabilities&service=WMS', version='1.1.1')
print wms_imerg.identification.type
print wms_imerg.identification.title

import requests
datasets_tutti = requests.get("http://ags.servirlabs.net/arcgis/rest/services/Global?f=pjson")
richiesta = datasets_tutti.json()['services']

for singolo in range(0,len(richiesta)):
    print richiesta[singolo]['name']

