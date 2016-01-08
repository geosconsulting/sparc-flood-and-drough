from dateutil import parser
import numpy as np
from osgeo import gdal, gdalnumeric
import os

gdal.UseExceptions()

def collect_prec_files_3b43(direttorio,mese_min, mese_max, anno):

    lista_files_climatology = []
    lista_files_present = []
    for (dirpath, dirnames, filenames) in os.walk(direttorio):
        for filename in filenames:
            dt = parser.parse(filename.split('.')[1])
            mese_derivato = int(dt.month)
            if str(anno) not in filename:
                if mese_derivato >= mese_min and mese_derivato <= mese_max:
                    lista_files_climatology.append(filename)
            else:
                if mese_derivato >= mese_min and mese_derivato <= mese_max:
                    lista_files_present.append(filename)

    return lista_files_climatology, lista_files_present


def genera_means(dir_base, lista_files, mese_min, mese_max, base_line):

        parte_date = str(mese_min) + "_" + str(mese_max) + "_" + str(base_line)
        nome_tif_mean = "trmm_3B43_17years_monthly/stats/mean_" + parte_date + ".tif"
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
            print "Processando file numero %s nome %s" % (indice_in_processo, file)
            file_attivo = gdal.Open(dir_base + file)
            banda = file_attivo.GetRasterBand(1)
            data = gdalnumeric.BandReadAsArray(banda)
            banda_somma = banda_somma + data
            indice_in_processo += 1
        mean_files = (banda_somma/(indice_in_processo-1))

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        raster_mean = driver.Create(nome_tif_mean, x_size, y_size, 1, type_banda_esempio)
        gdalnumeric.CopyDatasetInfo(file_per_stats, raster_mean)
        banda_dove_scrivere_raster_mean = raster_mean.GetRasterBand(1)

        try:
            gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_mean, mean_files)
            print "Mean raster exported in" + nome_tif_mean + "\n"
            return nome_tif_mean
        except IOError as err:
            return str(err.message) + + "\n"


def genera_std(dir_base, lista_files, mese_min, mese_max, file_mean,base_line):

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")

    parte_date = str(mese_min) + "_" + str(mese_max) + "_" + str(base_line)
    nome_tif_std = "trmm_3B43_17years_monthly/stats/std_" + parte_date + ".tif"
    print nome_tif_std

    num_files = len(lista_files)
    print "numero di files da processare " + str(num_files)

    file_base = lista_files[0]
    file_per_stats = gdal.Open(dir_base + file_base)
    x_size = file_per_stats.RasterXSize
    y_size = file_per_stats.RasterYSize
    numero_bande = file_per_stats.RasterCount
    banda_esempio = file_per_stats.GetRasterBand(1)
    type_banda_esempio = banda_esempio.DataType
    file_media = gdal.Open(file_mean)
    banda_media = file_media.GetRasterBand(1)
    data_media = gdalnumeric.BandReadAsArray(banda_media)

    banda_somma_squared = np.zeros((y_size, x_size,), dtype=np.float64)
    indice_in_processo = 1
    for file in lista_files:
        print "Processando file numero %s nome %s" % (indice_in_processo, file)
        file_attivo = gdal.Open(dir_base + file)
        banda_attiva = file_attivo.GetRasterBand(1)
        data = gdalnumeric.BandReadAsArray(banda_attiva)
        banda_sottrazione = gdalnumeric.square(data - data_media)
        banda_somma_squared = banda_somma_squared + banda_sottrazione
        indice_in_processo += 1

    std_file = gdalnumeric.sqrt(banda_somma_squared/(indice_in_processo-1))

    raster_std = driver.Create(nome_tif_std, x_size, y_size, 1,type_banda_esempio)
    gdalnumeric.CopyDatasetInfo(file_per_stats, raster_std)
    banda_dove_scrivere_raster_std = raster_std.GetRasterBand(1)

    try:
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_std, std_file)
        print "Standard Deviation raster exported in " + nome_tif_std + "\n"
        return nome_tif_std
    except IOError as err:
        return str(err.message) + "\n"

def spi(current_rain, climatology_mean,climatology_std, mask,mese_min,mese_max, anno):

    gdalnumeric.seterr(all='ignore')

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")

    parte_date = str(mese_min) + "_" + str(mese_max) + "_" + str(anno)
    nome_tif_spi = "trmm_3B43_17years_monthly/spi_data/spi_" + parte_date + ".tif"
    print nome_tif_spi

    file_cur_prec = gdal.Open(current_rain)
    file_media_clim = gdal.Open(climatology_mean)
    file_std_clim = gdal.Open(climatology_std)
    file_mask = gdal.Open(mask)

    x_size = file_cur_prec.RasterXSize
    y_size = file_cur_prec.RasterYSize

    banda_cur_prec = file_cur_prec.GetRasterBand(1)
    array_cur_prec = gdalnumeric.BandReadAsArray(banda_cur_prec)

    type_banda_esempio = banda_cur_prec.DataType

    banda_media_clim = file_media_clim.GetRasterBand(1)
    array_media_clim = gdalnumeric.BandReadAsArray(banda_media_clim)

    banda_std_clim = file_std_clim.GetRasterBand(1)
    array_clim_std = gdalnumeric.BandReadAsArray(banda_std_clim)

    banda_mask = file_mask.GetRasterBand(1)
    array_mask = gdalnumeric.BandReadAsArray(banda_mask)

    numeratore_banda_spi = gdalnumeric.subtract(array_cur_prec, array_media_clim)
    banda_spi = gdalnumeric.divide(numeratore_banda_spi, array_clim_std)
    # file_spi_mascherato = gdalnumeric.multiply(banda_spi, array_mask)

    raster_spi = driver.Create(nome_tif_spi, x_size, y_size, 1, type_banda_esempio)
    gdalnumeric.CopyDatasetInfo(file_cur_prec, raster_spi)
    banda_dove_scrivere_raster_spi = raster_spi.GetRasterBand(1)

    try:
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_spi, banda_spi)
        print "Standard Deviation raster exported in " + nome_tif_spi + "\n"
        return raster_spi
    except IOError as err:
        return str(err.message) + "\n"


anno = 2015
base_line = 9814
mese_min = 10
mese_max = 10
climatology, current = collect_prec_files_3b43('trmm_3B43_17years_monthly/convertiti/', mese_min, mese_max, anno)

print climatology
print current

mean_climatology = genera_means('trmm_3B43_17years_monthly/convertiti/', climatology, mese_min, mese_max,base_line)
std_climatology = genera_std('trmm_3B43_17years_monthly/convertiti/', climatology, mese_min, mese_max, mean_climatology,base_line)
mean_current = genera_means('trmm_3B43_17years_monthly/convertiti/', current, mese_min, mese_max, anno)
mask = 'trmm_3B43_17years_monthly/spi_data/masks/ca_mask.tif'

spi(mean_current, mean_climatology,std_climatology, mask,mese_min,mese_max, anno)