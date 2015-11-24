from owslib.wms import WebMapService
wms = WebMapService('http://chg-ewx.geog.ucsb.edu:8080/geoserver/ows?', version='1.3.0')
print wms.identification.type, wms.identification.title

#import matplotlib.pyplot as plt
list_layers = list(wms.contents)
for layer in list_layers:
    print layer
print wms.getOperationByName('GetCapabilities').methods


