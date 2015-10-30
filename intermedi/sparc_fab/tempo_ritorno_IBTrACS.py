# -*- coding: utf-8 -*
import os
from osgeo import ogr
ogr.UseExceptions()
import glob
import pycountry
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# COSTANTI
PROJ_DIR = "c:/sparc/projects/cyclones/"
DRIVER = ogr.GetDriverByName("ESRI Shapefile")
CYLONES_RECLASSED_DIR = "C:/sparc/input_data/cyclones_data/"
CYCLONES_TRACKS_DIR = "C:/sparc/input_data/cyclones_data/"
SHAPE_COUNTRIES = "c:/sparc/input_data/gaul/gaul_wfp_iso.shp"
SHAPE_TRACKS = CYCLONES_TRACKS_DIR + "cy_tracks.shp"

FIELD_NAME_COUNTRY = "ADM0_NAME"
FIELD_ISO_COUNTRY = "ADM0_CODE"
FIELD_NAME_ADMIN1 = "ADM1_NAME"
FIELD_ISO_ADMIN1 = "ADM1_CODE"
FIELD_NAME_ADMIN2 = "ADM2_NAME"
FIELD_ISO_ADMIN2 = "ADM2_CODE"
filter_field_cyclones = "gid,serial_num"

def file_structure_creation(admin_name, adm_code):

        os.chdir(PROJ_DIR)
        country_low = str(paese).lower()
        if os.path.exists(country_low):
            os.chdir(PROJ_DIR + country_low)
            admin_low = admin_name.lower() + "_" + str(adm_code)
            #print admin_low
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))
        else:
            os.chdir(PROJ_DIR)
            os.mkdir(country_low)
            os.chdir(PROJ_DIR + country_low)
            admin_low = admin_name.lower() + "_" + str(adm_code)
            #print admin_low
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))

        return "Project created......\n"

def extract_admin(shape_countries_pass,code_adm):

    shapefile_countries = DRIVER.Open(shape_countries_pass)
    layer_admins = shapefile_countries.GetLayer()

    # Get the input Layer
    inDataSource = DRIVER.Open(SHAPE_COUNTRIES, 0)
    inLayer = inDataSource.GetLayer()
    inLayerProj = inLayer.GetSpatialRef()
    inLayer.SetAttributeFilter("ADM2_CODE=" + code_adm)
    conteggio_admin = layer_admins.GetFeatureCount()

    # Create the output LayerS
    outShapefile = os.path.join(PROJ_DIR + code_adm + ".shp")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        DRIVER.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = DRIVER.CreateDataSource(outShapefile)
    out_lyr_name = str(code)
    out_layer = outDataSource.CreateLayer(out_lyr_name, inLayerProj, geom_type=ogr.wkbMultiPolygon)

    # Add input Layer Fields to the output Layer if it is the one we want
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        if fieldName not in FIELD_ISO_ADMIN2:
            continue
            out_layer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = out_layer.GetLayerDefn()

    # Add features to the ouput Layer
    for inFeature in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            fieldDefn = outLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            if fieldName not in FIELD_ISO_ADMIN2:
                continue
            dascrivere = inFeature.GetField(fieldName)
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), dascrivere)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom.Clone())

        # Add new feature to output Layer
        out_layer.CreateFeature(outFeature)

        print "Admin extracted......"

    # Close DataSources
    inDataSource.Destroy()
    outDataSource.Destroy()

    return conteggio_admin

def extract_cyclones(shape_tracks, adm):

    path_admin_exctracted = PROJ_DIR + adm + ".shp"
    print path_admin_exctracted
    shapefile_adm = DRIVER.Open(path_admin_exctracted)
    layer_admins = shapefile_adm.GetLayer()

    poly_adm2 = layer_admins.GetNextFeature()
    poly = poly_adm2.GetGeometryRef()

    shapefile_tracce = DRIVER.Open(shape_tracks)
    layer_tracks = shapefile_tracce.GetLayer()
    layer_tracks.SetSpatialFilter(poly)
    numero_tracce_selezionate = layer_tracks.GetFeatureCount()
    print "There are %d tracks selected" % (numero_tracce_selezionate)

    # Get the input Layer
    inDriver = DRIVER
    inDataSource = inDriver.Open(shape_tracks, 0)
    inLayer = inDataSource.GetLayer()
    inLayerProj = inLayer.GetSpatialRef()

    outShapefile = os.path.join(PROJ_DIR + str(code) + "_cy.shp")
    outDriver = DRIVER
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    out_lyr_name = str(code) + "_cy"
    out_layer = outDataSource.CreateLayer(out_lyr_name, inLayerProj, geom_type=ogr.wkbMultiLineString)

    # Add input Layer Fields to the output Layer if it is the one we want
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        # if fieldName not in filter_field_cyclones:
        #     continue
        #     out_layer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = out_layer.GetLayerDefn()

    # Add features to the ouput Layer
    for inFeature in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            fieldDefn = outLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            # if fieldName not in filter_field_cyclones:
            #     continue
            dascrivere = inFeature.GetField(fieldName)
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), dascrivere)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom.Clone())

        # Add new feature to output Layer
        out_layer.CreateFeature(outFeature)

    print "Cyclones extracted......"

        # Close DataSources
    inDataSource.Destroy()
    outDataSource.Destroy()

    return numero_tracce_selezionate

paese = pycountry.countries.get(alpha3 = 'PHL')
iso = paese.alpha3
nome_paese = paese.name
code = 24216

extract_admin(SHAPE_COUNTRIES, str(code))
extract_cyclones(SHAPE_TRACKS, str(code))

# print "Ci sono %d tracce che intersecano %d poligoni " % (numero_tracce, num_admin)
#
# nomi = set()
# anni = set()
#
# feature = layer_tracks.GetNextFeature()
# while feature:
#     nomi.add(feature.other_name)
#     anni.add(feature.year)
#     feature = layer_tracks.GetNextFeature()
#
# num_evts = 1
# sum_rps = 0
#
# dict_anni = {}
# for anno in anni:
#     dict_anni[num_evts] = anno
#     num_evts +=1
#
# for chiave, anno in dict_anni.iteritems():
#     # print dict_anni[chiave]
#     if chiave>1:
#         indice1 = chiave-1
#         indice2 = chiave
#         differenza = abs(dict_anni[indice1] - dict_anni[indice2])
#         sum_rps = sum_rps +  differenza
#
# os.chdir(CYLONES_RECLASSED_DIR)
# category_reclass_yearly_tifs = glob.glob("*.tif")

###PLOTTING EXCTRACTED CYCLONES
# map = Basemap(llcrnrlon=-0.5,llcrnrlat=39.8,urcrnrlon=4.,urcrnrlat=43.,
#              resolution='i', projection='tmerc', lat_0 = 39.5, lon_0 = 1)
#
# map.drawmapboundary(fill_color='aqua')
# map.fillcontinents(color='#ddaa66',lake_color='aqua')
# map.drawcoastlines()
#
# map.readshapefile('../sample_files/comarques', 'comarques')
#
# plt.show()

