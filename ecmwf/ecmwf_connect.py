from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

import fiona

from osgeo import gdal, gdalnumeric, ogr, osr
import PIL
import os, sys
gdal.UseExceptions()

def caratteristiche_shp(file_shp):


    ilVettore = fiona.open(file_shp)
    laProiezioneDelVettore = ilVettore.crs
    laBoundingBox = ilVettore.bounds

    return laProiezioneDelVettore, laBoundingBox

def fetch_ECMWF_data(file_output, time_frame, area_richiesta):

    print time_frame
    north = area_richiesta[3]
    west = area_richiesta[0]
    south = area_richiesta[1]
    east = area_richiesta[2]
    illo = str(north) + "/" + str(west) + "/" + str(south) + "/" + str(east)
    print illo

    # request FABIO
    # server.retrieve({
    #     "class": "s2",
    #     "dataset": "s2s",
    #     "date": "2015-01-01/to/2015-01-31",
    #     "expver": "prod",
    #     "levtype": "sfc",
    #     "origin": "kwbc",
    #     "param": "165",
    #     "step": "24/to/1056/by/24",
    #     "stream": "enfo",
    #     "target": "temp1.grib",
    #     "time": "00",
    #     "number": "1/to/15",
    #     "type": "cf",
    #  })

    # request WFP
    server.retrieve({
        "class": "ei",
        "dataset": "interim",
        "date": time_frame,
        "expver": "1",
        # "grid": "0.75/0.75",
        "grid": "0.125/0.125",
        "levtype": "sfc",
        "param": "228.128",
        "step": "12",
        "stream": "oper",
        # "area": "E",
         "area" : illo,
        "target": file_output,
        # "format": "netcdf",
        "time": "12",
        "type": "fc",
    })

def apriRaster(raster):
    try:
        src_ds = gdal.Open(raster)
    except RuntimeError, e:
        print 'Unable to open raster file'
        print e
        sys.exit(1)

    return src_ds

def rasterStats(raster):

    print "[ RASTER BAND COUNT ]: ", raster.RasterCount
    lista_bande = []

    for band in range(raster.RasterCount):
        band += 1
        print "[GETTING BAND]: ", band
        srcband = raster.GetRasterBand(band)
        lista_bande.append(srcband)
        if srcband is None:
            continue

        stats = srcband.GetStatistics(True, True)
        if stats is None:
            pass

        print "Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
        print "NO DATA VALUE = ", srcband.GetNoDataValue()
        print "MIN = ", srcband.GetMinimum()
        print "MAX = ", srcband.GetMaximum()
        print "SCALE = ", srcband.GetScale()
        print "UNIT TYPE = ", srcband.GetUnitType()

def taglia_raster(banda):

    #
    #  create output datasource
    #
    dst_layername = "POLYGONIZED_STUFF"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(dst_layername + ".shp" )
    dst_layer = dst_ds.CreateLayer(dst_layername, srs = None )

    gdal.Polygonize(banda, None, dst_layer, -1, [], callback=None )

def Usage():

    print("example run : $ python getting_grib_files.py /<full-path>/<shapefile-name>.shp /<full-path>/<raster-name>.tif 2015-07-31 2015-08-30")
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 4:
        Usage()
        sys.exit(1)

    raster_file = sys.argv[1]
    vector_file = sys.argv[2]
    data_minima = str(sys.argv[3])
    data_massima = str(sys.argv[4])

    if os.path.isfile(sys.argv[1]):
        print "ECMWF file exists change the name of the output grib file"
        pass
    else:
        # "2015-07-31/to/2015-08-30"
        time_frame = data_minima + "/to/" + data_massima
        proiezione, area_richiesta = caratteristiche_shp(vector_file)
        fetch_ECMWF_data(raster_file, time_frame, area_richiesta)
        # raster = apriRaster(raster_file)
        # rasterStats(raster)