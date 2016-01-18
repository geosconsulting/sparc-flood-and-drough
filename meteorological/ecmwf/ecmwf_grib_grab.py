from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

import calculate_time_window_date


import json
import fiona
import numpy as np
from osgeo import gdal, gdalnumeric
import sys
gdal.UseExceptions()

def Usage():

    print("example run : $ python ecmwf_data_analysis.py country name")
    sys.exit(1)

def Shp_BBox(file_shp):

    ilVettore = fiona.open(file_shp)
    laProiezioneDelVettore = ilVettore.crs
    laBoundingBox = ilVettore.bounds

    return laProiezioneDelVettore, laBoundingBox

def fetch_ECMWF_data(file_output, time_frame, dict_area_richiesta):

    date = open(time_frame)
    time_frame_json = json.load(date)

    north = round(float(dict_area_richiesta['ymax'])*2/2)
    west = round(float(dict_area_richiesta['xmin'])*2/2)
    south = round(float(dict_area_richiesta['ymin'])*2/2)
    east = round(float(dict_area_richiesta['xmax'])*2/2)
    area_ecmwf_bbox = str(north) + "/" + str(west) + "/" + str(south) + "/" + str(east)

    # request WFP UN MESE ERA-Interim, Daily
    # server.retrieve({
    #     "class": "ei",
    #     "dataset": "interim",
    #     "date": time_frame_json,
    #     "expver": "1931",
    #     "grid": "0.125/0.125",
    #     "levtype": "sfc",
    #     "param": "228.128",
    #     "step": "12",
    #     "stream": "mdfa",
    #     "area": area_ecmwf_bbox,
    #     "target": file_output,
    #     "time": "12",
    #     "type": "fc",
    # })

    # day 1 to day 7 (STEP=0-168)*
    # day 5 to day 11 (STEP=96-264)
    # day 8 to day 14 (STEP=168-336)*
    # day 12 to day 18 (STEP=264-432)
    # day 15 to day 21 (STEP=336-504)*
    # day 19 to day 25 (STEP=432-600)
    # day 21 to 28 (STEP=504 to 672) *
    # day 26 to day 32 (STEP=600-768)
    # * archived only since 10 October 2011 (additional monthly forecasts on Monday)

    # retrieve,stream=enfo,time=00,levtype=sfc,expver=0001,param=139.131, quantile=1:3,class=od,date=20131205,step=96-264,type=pd,target="out"

    server.retrieve({
        "class": "od",
        "dataset": "interim",
        "date": "20051013",
        "quantile": "1:3",
        "levtype": "sfc",
        "param": "228.131",
        "step": "96-264", #from day 8 to day 14
        "stream": "enfo",
        "expver": "0001",
        # "expect": "any",
        # "area": area_ecmwf_bbox,
        "time": "00",
        "type": "pd",
        "target": file_output
    })

    return "Grib file generated in" + file_output + "\n"


def genera_statistiche_banda_grib(banda, indice):

    print
    print "DATA FOR BAND", indice
    stats = banda.GetStatistics(True, True)
    if stats is None:
        pass

    print "Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
    print "NO DATA VALUE = ", banda.GetNoDataValue()
    print "MIN = ", banda.GetMinimum()
    print "MAX = ", banda.GetMaximum()
    print "SCALE = ", banda.GetScale()
    print "UNIT TYPE = ", banda.GetUnitType()


# if __name__ == '__main__':

    # if len(sys.argv) < 1:
    #     Usage()
    #     sys.exit(1)
    #
    # vector_file = "c:/sparc/input_data/countries/" + sys.argv[1] + ".shp"
    # paese = vector_file.split(".")[0].split("/")[-1]

    # ritornato = calculate_time_window_date.scateniamo_l_inferno(paese)
    # parte_date = ritornato.split("/")[1].split(".")[0][4:]
    # tre_lettere = vector_file.split(".")[0].split("/")[-1][0:3]
    # raster_file = "gribs/historical/" + tre_lettere + parte_date + ".grib"
    # print raster_file
    #
    # if os.path.isfile(raster_file):
    #     print "grib esiste"
    #     genera_means(raster_file)
    # else:
    #     print "grib non esiste"
    #     genera_gribs(ritornato, vector_file, raster_file)
    #     genera_means(raster_file)
    #

dict = {'ymax': '15', 'xmin': '-90','ymin': '-20', 'xmax': '-65'}

# fetch_ECMWF_data("c:/temp/tt1.grib",'dates/req_0817_12_19732012.txt',dict)

fetch_ECMWF_data("gribs/probabilities/prob_test.grib", "dates/req_20131205.txt", dict)
