import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from osgeo import gdalnumeric
gdal.UseExceptions()
from ftplib import FTP

driver = gdal.GetDriverByName("GTiff")

ftp = FTP('ftp.wfp.org')
ftp.login('WFP_GISviewer','FTPviewer')
# print ftp.getwelcome()
# lista_files = ftp.retrlines('LIST')
ftp.close()

file_10days_ecmwf = "ecmwf_ftp_wfp/A1D12020000121200001.grib"
arr_10_days = gdalnumeric.LoadFile(file_10days_ecmwf)
grib_file_10days = gdal.Open(file_10days_ecmwf, GA_ReadOnly)

x_size = grib_file_10days.RasterXSize
y_size = grib_file_10days.RasterYSize
numero_bande = grib_file_10days.RasterCount

for numero_banda in range(1, numero_bande + 1):
    banda_corrente = grib_file_10days.GetRasterBand(numero_banda)
    metadati = banda_corrente.GetMetadata()
    if(metadati['GRIB_ELEMENT'] == 'TP'):
        print metadati
        type_banda_esempio = banda_corrente.DataType
        valori_prec_10Days = arr_10_days[numero_banda]
        banda_TP_tif_file = "ecmwf_ftp_wfp/TP_0212.tif"
        # Write the out file
        raster_TP_from_GRIB = driver.Create(banda_TP_tif_file, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(grib_file_10days, raster_TP_from_GRIB)
        banda_dove_scrivere_raster_mean = raster_TP_from_GRIB.GetRasterBand(1)
        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, valori_prec_10Days)
            print "Anomalies 10 days raster exported"
        except IOError as err:
            print err.message
        break

