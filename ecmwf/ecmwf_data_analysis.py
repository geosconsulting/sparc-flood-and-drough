from ecmwfapi import ECMWFDataServer
server = ECMWFDataServer()

import calculate_time_window_date
import extract_total_precipitation_hres

import json
import fiona
import numpy as np
from osgeo import gdal, gdalnumeric
import os
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

def fetch_ECMWF_data(file_output, time_frame, area_richiesta):

    north = area_richiesta[3]
    west = area_richiesta[0]
    south = area_richiesta[1]
    east = area_richiesta[2]
    illo = str(north) + "/" + str(west) + "/" + str(south) + "/" + str(east)

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

def genera_gribs(ritornato, vector_file, raster_file):

    date = open(ritornato)
    time_frame = json.load(date)
    print time_frame
    proiezione, area_richiesta = Shp_BBox(vector_file)
    fetch_ECMWF_data(raster_file, time_frame, area_richiesta)

def genera_means(file_path):

        print "ECMWF file exists calculating statistics"
        print "Change the name of the output grib file for fetching new data"
        nome_tif_mean = "calc/historical/mean_" + tre_lettere + parte_date + ".tif"

        ecmfwf_file_asRaster = gdal.Open(file_path)
        x_size =  ecmfwf_file_asRaster.RasterXSize
        y_size = ecmfwf_file_asRaster.RasterYSize
        numero_bande = ecmfwf_file_asRaster.RasterCount
        # print "Ci sono %d bande " % numero_bande
        banda_esempio = ecmfwf_file_asRaster.GetRasterBand(1)
        type_banda_esempio = banda_esempio.DataType

        banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
        for i in range(1, numero_bande):
            banda = ecmfwf_file_asRaster.GetRasterBand(i)
            # NON MI SERVE IN QUESTA FASE MA E' UTILE IN PROSPETTIVA
            # genera_statistiche_banda_grib(banda, i)
            data = gdalnumeric.BandReadAsArray(banda)
            banda_somma = banda_somma + data
        # mean_bande_in_mm = (banda_somma/numero_bande)*1000
        # CONFRONTANDO FORECAST CON FORECAST NON HO BISOGNO DI AVERLO IN MILLIMETRI LASCIO TUTTO IN METRI
        mean_bande_in_mm = (banda_somma/numero_bande)

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_mean_from_bands = driver.Create(nome_tif_mean, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(ecmfwf_file_asRaster, raster_mean_from_bands)
        banda_dove_scrivere_raster_mean = raster_mean_from_bands.GetRasterBand(1)
        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_bande_in_mm)
            print "mean raster exported"
        except IOError as err:
            print err.message

def analisi_raster_con_GDALNUMERICS(nome_tif_mean):

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
    ritornato = calculate_time_window_date.scateniamo_l_inferno(paese)
    parte_date = ritornato.split("/")[1].split(".")[0][4:]
    tre_lettere = vector_file.split(".")[0].split("/")[-1][0:3]
    raster_file = "gribs/historical/" + tre_lettere + parte_date + ".grib"

    # CONNESSIONE A FTP SCARICO DATI E ESTRAZIONE BANDA PRECIPITAZIONE TOTALE
    extract_total_precipitation_hres.FtpWork()
    extract_total_precipitation_hres.estrazione_banda_TP_hres("ecmwf_ftp_wfp/A1D12020000121200001.grib","ecmwf_ftp_wfp/TP_0212")

    if os.path.isfile(raster_file):
        print "grib esiste"
        genera_means(raster_file)
    else:
        print "grib non esiste"
        genera_gribs(ritornato, vector_file, raster_file)
        genera_means(raster_file)

