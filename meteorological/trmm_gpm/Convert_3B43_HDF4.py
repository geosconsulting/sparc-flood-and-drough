import numpy as np
from pyhdf.SD import SD, SDC
import os

from osgeo import gdal
import glob
import sys

def convert_mese_trmm_3b43(FILE_NAME, FILE_EXTENSION):

    # Open file.
    FILE_NAME_COMPLETO = "trmm_3B43_17years_monthly/" + FILE_NAME + FILE_EXTENSION
    print FILE_NAME
    hdf = SD(FILE_NAME_COMPLETO, SDC.READ)

    # Read dataset
    DATAFIELD_NAME = 'precipitation'
    pioggia = hdf.select(DATAFIELD_NAME)
    data_contr = np.array(pioggia.get()[::-1])
    data_tra = np.transpose(data_contr)
    data_up = np.flipud(data_tra)
    data = np.fliplr(data_up)
    # size_pioggia = data.shape

    FileASC = "trmm_3B43_17years_monthly/convertiti/" + FILE_NAME + ".asc"

    ascii_file = open(FileASC, 'w')
    header0 = 'ncols 1440'
    header1 = 'nrows 400'
    header2 = 'xllcorner -180'
    header3 = 'yllcorner -50'
    header4 = 'cellsize 0.25'
    header5 = 'NODATA_value -99999.00'
    ascii_file.write(header0 + "\n")
    ascii_file.write(header1 + "\n")
    ascii_file.write(header2 + "\n")
    ascii_file.write(header3 + "\n")
    ascii_file.write(header4 + "\n")
    ascii_file.write(header5 + "\n")
    formato = "{0} "
    for i in range(0, 400):
        for j in range(0, 1440):
            ascii_file.write(formato.format(data[i, j]))
        ascii_file.write("\n")
    ascii_file.close()

def convert_asc_2_tif(DIR_ASC, FILE_NAME, DIR_TIF):

    FORMAT_IN = '.asc'
    FORMAT_OUT = '.tif'
    DRV = gdal.GetDriverByName('GTiff')

    # Open file.
    FILE_NAME_COMPLETO_IN = DIR_ASC + FILE_NAME + FORMAT_IN
    FILE_NAME_COMPLETO_OUT = DIR_TIF + FILE_NAME + FORMAT_OUT
    print FILE_NAME_COMPLETO_IN, FILE_NAME_COMPLETO_OUT

    ds_in = gdal.Open(FILE_NAME_COMPLETO_IN)
    ds_out = DRV.CreateCopy(FILE_NAME_COMPLETO_OUT, ds_in)
    ds_in = None
    ds_out = None

def collect_prec_files_3b43(direttorio):

    lista_files = []
    for (dirpath, dirnames, filenames) in os.walk(direttorio):
        lista_files.extend(filenames)
        break
    return lista_files

DIR_HDF = 'trmm_3B43_17years_monthly/scaricati_mirador/'
DIR_ASC = 'trmm_3B43_17years_monthly/convertiti/'
DIR_TIF = 'trmm_3B43_17years_monthly/convertiti_tif/'

ritornati = collect_prec_files_3b43(DIR_HDF)


for ritornato in ritornati:
    filename, file_extension = os.path.splitext(ritornato)
    if file_extension == '.HDF':
        #convert_mese_trmm_3b43(filename, file_extension)
        convert_asc_2_tif(DIR_ASC,filename,DIR_TIF)