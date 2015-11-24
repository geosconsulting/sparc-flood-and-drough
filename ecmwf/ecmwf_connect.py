from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

import genera_date

import json
import fiona
import numpy as np
import pandas as pd
from osgeo import gdal, gdalnumeric
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

    file_output = file_output

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

    # # request WFP
    # server.retrieve({
    #     "class": "ei",
    #     "dataset": "interim",
    #     "date": time_frame,
    #     "expver": "1",
    #     # "grid": "0.75/0.75",
    #     "grid": "0.125/0.125",
    #     "levtype": "sfc",
    #     "param": "228.128",
    #     "step": "12",
    #     "stream": "oper",
    #     # "area": "E",
    #      "area" : illo,
    #     "target": file_output,
    #     # "format": "netcdf",
    #     "time": "12",
    #     "type": "fc",
    # })

    # request WFP UN MESE ERA-Interim, Daily
    server.retrieve({
        "class": "ei",
        "dataset": "interim",
        "date": time_frame,
        "expver": "1931",
        "grid": "0.125/0.125",
        "levtype": "sfc",
        "param": "228.128",
        "step": "12",
        "stream": "mdfa",
        "area": illo,
        "target": file_output,
        "time": "12",
        "type": "fc",
    })

    # # request WFP Hindcast 2015 November
    # server.retrieve({
    #     "class": "od",
    #     "dataset": "interim",
    #     "date": "=2015-05-11",
    #     "expver": "67",
    #     "grid": "0.125/0.125",
    #     "levtype": "sfc",
    #     "param": "228.128",
    #     "step" : "0-24/0-72/0-120/0-240/0-360/12-36/12-84/12-132/24-48/24-96/24-144/36-60/36-108/36-156/48-72/48-120/48-168/60-84/60-132/60-180/72-96/72-144/72-192/84-108/84-156/84-204/96-120/96-168/96-216/108-132/108-180/108-228/120-144/120-192/132-156/132-204/144-168/144-216/156-180/156-228/240-360",
    #     "stream" : "efhs",
    #     "target": "gribs/test.grib",
    #     "time": "00",
    #     "type": "cd",
    # })


def apriRaster(raster):
    try:
        src_ds = gdal.Open(raster)
    except RuntimeError, e:
        print 'Unable to open raster file'
        print e
        sys.exit(1)

    return src_ds

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

def plotRasterHistogram(file_mean):

    #Open the dataset
    ds1 = gdal.Open(file_mean)
    banda = ds1.GetRasterBand(1)
    dati = gdalnumeric.BandReadAsArray(banda)
    print dati

def Usage():

    print("example run : $ python ecmwf_connect.py country name")
    sys.exit(1)


def genera_gribs(ritornato,vector_file,raster_file):

    date = open(ritornato)
    time_frame = json.load(date)
    proiezione, area_richiesta = caratteristiche_shp(vector_file)
    fetch_ECMWF_data(raster_file, time_frame, area_richiesta)


def genera_means(file_path):

        print "ECMWF file exists calculating statistics"
        print "Change the name of the output grib file for fetching new data"
        nome_tif_mean = "calc/historical/mean_" + tre_lettere + parte_date + ".tif"

        ecmfwf_file_asRaster = gdal.Open(file_path)
        x_size =  ecmfwf_file_asRaster.RasterXSize
        y_size = ecmfwf_file_asRaster.RasterYSize
        numero_bande = ecmfwf_file_asRaster.RasterCount
        banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
        type_banda_esempio = banda_esempio.DataType

        banda_somma = np.zeros((y_size, x_size,), dtype= np.float64)
        print "Dimensione raster somma %d " % banda_somma.ndim
        for i in range(1, numero_bande):
            banda = ecmfwf_file_asRaster.GetRasterBand(i)
            genera_statistiche_banda_grib(banda, i)
            data = gdalnumeric.BandReadAsArray(banda)
            banda_somma = banda_somma + data
        # mean_bande_in_mm = (banda_somma/numero_bande)*1000
        # CONFRONTANDO FORECAST CON FORECAST NON HO BISOGNO DI AVERLO IN MILLIMETRI LACIO TUTTO IN METRI
        mean_bande_in_mm = (banda_somma/numero_bande)

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_mean_from_bands = driver.Create(nome_tif_mean, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_mean_from_bands)
        banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_bande_in_mm)

def analisi_raster_con_GDALNUMERICS(nome_tif_mean):

        pass

        plotRasterHistogram(nome_tif_mean)
        # PRIMO TENTATIVO CON GDALNUMERIC CREA SOLO MAGGIORE CONFUSIONE PREFERISCO ANDARE CON GDAL

        arr = gdalnumeric.LoadFile(raster_file)
        righe, colonne = arr.shape[1], arr.shape[2]
        print "mean", arr.mean()

        numero_bande = len(arr)
        banda_somma = np.zeros((righe, colonne))
        for i in range(0, numero_bande):
             banda_somma = banda_somma + arr[i]
        mean_bande = banda_somma/numero_bande

        # PRIMO TENTATIVO CON GDALNUMERIC CREA SOLO MAGGIORE CONFUSIONE PREFERISCO ANDARE CON GDAL

if __name__ == '__main__':

    if len(sys.argv) < 1:
        Usage()
        sys.exit(1)

    vector_file = "c:/sparc/input_data/countries/" + sys.argv[1] + ".shp"
    paese = vector_file.split(".")[0].split("/")[-1]
    ritornato = genera_date.crea_file(paese)
    parte_date = ritornato.split("/")[1].split(".")[0][4:]
    tre_lettere = vector_file.split(".")[0].split("/")[-1][0:3]
    raster_file = "gribs/historical/" + tre_lettere + parte_date + ".grib"

    if os.path.isfile(raster_file):
        genera_means(raster_file)
    else:
        genera_gribs(ritornato, vector_file, raster_file)
        genera_means(raster_file)

