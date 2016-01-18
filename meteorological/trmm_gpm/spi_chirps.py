import numpy as np
from osgeo import gdal, gdalnumeric
gdal.UseExceptions()
from netCDF4 import Dataset

nc_file = '../chirps/chirps-v2.0.monthly.nc'

file_per_stats = gdal.Open(nc_file)
x_size = file_per_stats.RasterXSize
y_size = file_per_stats.RasterYSize
numero_bande = file_per_stats.RasterCount
banda_esempio = file_per_stats.GetRasterBand(1)
type_banda_esempio = banda_esempio.DataType

print x_size, y_size, numero_bande, banda_esempio, type_banda_esempio

rootgrp = Dataset(nc_file, mode='r')
import matplotlib.pyplot as plt
#print "Data Model " + rootgrp.data_model
#print rootgrp.groups.values

variabili = rootgrp.variables
print variabili.keys()

# subset and subsample
# lon = variabili['longitude'][:]
# lat = variabili['latitude'][:]
# read the 1st time step
# itime = 0
# tair = variabili['precip'][itime,:]
#
# plt.pcolormesh(lon, lat, tair)
# plt.colorbar()
# plt.show()

# print variabili
# print variabili['precip']

lons = rootgrp.variables['longitude'][:]
lats = rootgrp.variables['latitude'][:]
precipitazioni = rootgrp.variables['precip']

# print precipitazioni.units
# print precipitazioni.long_name
numero_osservazioni = precipitazioni.shape[0]
x_size = precipitazioni.shape[2]
y_size = precipitazioni.shape[1]

# for name in rootgrp.ncattrs():
#     print 'Global attr', name, '=', getattr(rootgrp,name)

banda_somma = np.zeros((y_size, x_size,), dtype=np.float64)
indice_in_processo = 1
for osservazione in range(0, numero_osservazioni):
    data = rootgrp.variables['precip'][osservazione]
    print "Processando file numero %s" % (indice_in_processo)
    banda_somma = banda_somma + data
    indice_in_processo += 1

banda_media = (banda_somma/(indice_in_processo-1))

nome_tif_mean = "../chirps/spi/mean_chirps.tif"
print nome_tif_mean

# Write the out file
driver = gdal.GetDriverByName("GTiff")
raster_mean = driver.Create(nome_tif_mean, y_size, x_size, 1, type_banda_esempio)
banda_dove_scrivere_raster_mean = raster_mean.GetRasterBand(1)

try:
    gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, banda_media)
    print "Mean raster exported in" + nome_tif_mean + "\n"
except IOError as err:
    print err.message + "\n"

# nome_tif_std = "trmm_3B43_17years_monthly/spi_calc/std_chirps.tif"
# print nome_tif_std
#
# banda_somma_squared = np.zeros((y_size, x_size,), dtype=np.float64)
# indice_in_processo_sd = 1
# for osservazione in range(0, numero_osservazioni):
#     print "Processando file numero %s nome %s" % (indice_in_processo, file)
#     file_attivo = gdal.Open(dir_base + file)
#     banda_esempio = file_attivo.GetRasterBand(1)
#     data = gdalnumeric.BandReadAsArray(banda_attiva)
#     banda_sottrazione = gdalnumeric.square(data - data_media)
#     banda_somma_squared = banda_somma_squared + banda_sottrazione
#     indice_in_processo += 1
#
# std_file = gdalnumeric.sqrt(banda_somma_squared/(indice_in_processo-1))
#
# raster_std = driver.Create(nome_tif_std, x_size, y_size, 1, type_banda_esempio)
# gdalnumeric.CopyDatasetInfo(file_per_stats, raster_std)
# banda_dove_scrivere_raster_std = raster_std.GetRasterBand(1)
#
# try:
#     gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_std, std_file)
#     print "Standard Deviation raster exported in " + nome_tif_std + "\n"
# except IOError as err:
#     print str(err.message) + "\n"

rootgrp.close()
