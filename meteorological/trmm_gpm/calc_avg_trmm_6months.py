import os
from dateutil import parser
import json
import fiona
import numpy as np
from osgeo import gdal, gdalnumeric
import os
import sys
gdal.UseExceptions()

def collect_prec_files_3b43(direttorio, mese_min, mese_max):

    lista_files = []
    for (dirpath, dirnames, filenames) in os.walk(direttorio):
        for filename in filenames:
            dt = parser.parse(filename.split('.')[1])
            mese_derivato = int(dt.month)
            if mese_derivato >= mese_min and mese_derivato <= mese_max:
                lista_files.append(filename)

    return lista_files

def genera_means(dir_base,lista_files, mese_min,mese_max):

        parte_date = str(mese_min) + "_" + str(mese_max)
        nome_tif_mean = "trmm_3B43_17years_monthly/medie/mean_" + parte_date + ".tif"
        print nome_tif_mean
        num_files= len(lista_files)
        print "numero di files da processare " + str(num_files)
        

        file_base = lista_files[0]
        file_per_stats = gdal.Open(dir_base + file_base)
        x_size = file_per_stats.RasterXSize
        y_size = file_per_stats.RasterYSize
        numero_bande = file_per_stats.RasterCount

        banda_esempio = file_per_stats.GetRasterBand(1)
        type_banda_esempio = banda_esempio.DataType
        banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)

        indice_in_processo = 1
        for file in lista_files:
            print "Processando file numero %s nome %s" % (indice_in_processo,file)
            file_attivo = gdal.Open(dir_base + file)
            banda = file_attivo.GetRasterBand(1)           
            data = gdalnumeric.BandReadAsArray(banda)
            banda_somma = banda_somma + data
            indice_in_processo += 1
        mean_files = (banda_somma/num_files)
        
        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_mean = driver.Create(nome_tif_mean, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(file_per_stats, raster_mean)
        banda_dove_scrivere_raster_mean = raster_mean.GetRasterBand(1)
        
        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_files)
            return "Mean raster exported in" + nome_tif_mean + "\n"
        except IOError as err:
            return str(err.message) + + "\n"

mese_min = 3
mese_max = 8
ritornati = collect_prec_files_3b43('trmm_3B43_17years_monthly/convertiti/', mese_min, mese_max)
genera_means('trmm_3B43_17years_monthly/convertiti/', ritornati, mese_min, mese_max)