from dateutil import parser
import numpy as np
from osgeo import gdal, gdalnumeric, ogr, osr
import os, sys
import Image, ImageDraw
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
        nome_tif_mean = "trmm_3B43_17years_monthly/spi_calc/mean_" + parte_date + ".tif"
        print nome_tif_mean
        num_files = len(lista_files)
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
            return str(err.message) + "\n"


def genera_std(dir_base, lista_files, mese_min, mese_max, file_mean,base_line):

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")

    parte_date = str(mese_min) + "_" + str(mese_max) + "_" + str(base_line)
    nome_tif_std = "trmm_3B43_17years_monthly/spi_calc/std_" + parte_date + ".tif"
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

    raster_std = driver.Create(nome_tif_std, x_size, y_size, 1, type_banda_esempio)
    gdalnumeric.CopyDatasetInfo(file_per_stats, raster_std)
    banda_dove_scrivere_raster_std = raster_std.GetRasterBand(1)

    try:
        gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_std, std_file)
        print "Standard Deviation raster exported in " + nome_tif_std + "\n"
        return nome_tif_std
    except IOError as err:
        return str(err.message) + "\n"


def spi(current_rain, climatology_mean, climatology_std, mese_min_pass, mese_max_pass, anno_pass, spi_frame_pass):

    gdalnumeric.seterr(all='ignore')

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")

    parte_date = str(mese_min_pass) + "_" + str(mese_max_pass) + "_" + str(anno_pass)
    nome_tif_spi = "trmm_3B43_17years_monthly/spi_calc/spi_" + str(spi_frame_pass) + "_" + parte_date + ".tif"
    print nome_tif_spi

    file_cur_prec = gdal.Open(current_rain)
    file_media_clim = gdal.Open(climatology_mean)
    file_std_clim = gdal.Open(climatology_std)

    x_size = file_cur_prec.RasterXSize
    y_size = file_cur_prec.RasterYSize

    banda_cur_prec = file_cur_prec.GetRasterBand(1)
    array_cur_prec = gdalnumeric.BandReadAsArray(banda_cur_prec)

    type_banda_esempio = banda_cur_prec.DataType

    banda_media_clim = file_media_clim.GetRasterBand(1)
    array_media_clim = gdalnumeric.BandReadAsArray(banda_media_clim)

    banda_std_clim = file_std_clim.GetRasterBand(1)
    array_clim_std = gdalnumeric.BandReadAsArray(banda_std_clim)

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


def spi_cut_shp(shapefile_path, raster_path):

    # This function will convert the rasterized clipper shapefile to a mask for use within GDAL.
    def imageToArray(i):
        """
        Converts a Python Imaging Library array to a
        gdalnumeric image.
        """
        # a = gdalnumeric.fromstring(i.tostring(),'b')
        a = gdalnumeric.fromstring(i.tobytes(),'b')
        a.shape = i.im.size[1], i.im.size[0]
        return a

    def arrayToImage(a):
        """
        Converts a gdalnumeric array to a
        Python Imaging Library Image.
        """
        i=Image.fromstring('L', (a.shape[1], a.shape[0]), (a.astype('b')).tostring())
        return i

    def world2Pixel(geoMatrix, x, y):
        """
        Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
        the pixel location of a geospatial coordinate
        """
        ulX = geoMatrix[0]
        ulY = geoMatrix[3]
        xDist = geoMatrix[1]
        yDist = geoMatrix[5]
        rtnX = geoMatrix[2]
        rtnY = geoMatrix[4]
        pixel = int((x - ulX) / xDist)
        line = int((ulY - y) / xDist)
        return pixel, line

    #
    #  EDIT: this is basically an overloaded
    #  version of the gdal_array.OpenArray passing in xoff, yoff explicitly
    #  so we can pass these params off to CopyDatasetInfo
    #
    def OpenArray( array, prototype_ds = None, xoff=0, yoff=0 ):

        ds = gdal.Open( gdalnumeric.GetArrayFilename(array) )

        if ds is not None and prototype_ds is not None:
            if type(prototype_ds).__name__ == 'str':
                prototype_ds = gdal.Open( prototype_ds )
            if prototype_ds is not None:
                gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff )
        return ds

    def histogram(a, bins=range(0,256)):
        """
       Histogram function for multi-dimensional array.
       a = array
       bins = range of numbers to match
       """

        fa = a.flat
        n = gdalnumeric.searchsorted(gdalnumeric.sort(fa), bins)
        n = gdalnumeric.concatenate([n, [len(fa)]])
        hist = n[1:] - n[:-1]
        return hist

    def stretch(a):

        """
        Performs a histogram stretch on a gdalnumeric array image.
        """
        hist = histogram(a)
        im = arrayToImage(a)
        lut = []
        for b in range(0, len(hist), 256):
            # step size
            step = reduce(operator.add, hist[b:b+256]) / 255
            # create equalization lookup table
            n = 0
            for i in range(256):
                lut.append(n / step)
                n = n + hist[i+b]
        im = im.point(lut)
        return imageToArray(im)


    # Load the source data as a gdalnumeric array
    srcArray = gdalnumeric.LoadFile(raster_path)

    # Also load as a gdal image to get geotransform (world file) info
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    # Create an OGR layer from a boundary shapefile
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer(os.path.split(os.path.splitext(shapefile_path)[0])[1])
    poly = lyr.GetNextFeature()

    # Convert the layer extent to image pixel coordinates
    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    # Calculate the pixel size of the new image
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)
    # clip = srcArray[:, ulY:lrY, ulX:lrX]
    # clip = srcArray[ulY:lrY, ulX:lrX]
    clip = srcArray[ulY:lrY, ulX:lrX]

    # EDIT: create pixel offset to pass to new image Projection info
    xoffset = ulX
    yoffset = ulY

    print "Xoffset , Yoffset = ( %f, %f )" % (xoffset, yoffset)

    # Create a new geomatrix for the image
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    # Map points to pixels for drawing the
    # boundary on a blank 8-bit,
    # black and white, mask image.
    points = []
    pixels = []
    geom = poly.GetGeometryRef()
    pts_poly = geom.GetGeometryRef(0)
    pts = pts_poly.GetGeometryRef(0)
    conteggio = pts.GetPointCount()

    for p in range(pts.GetPointCount()):
        points.append((pts.GetX(p), pts.GetY(p)))

    for p in points:
        pixels.append(world2Pixel(geoTrans, p[0], p[1]))

    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)

    # Clip the image using the mask
    clip = gdalnumeric.choose(mask, (clip, 0)).astype(gdalnumeric.uint8)

    # This image has 3 bands so we stretch each one to make them
    # visually brighter
    for i in range(3):
        # clip[i, :, :] = stretch(clip[i, :, :])
        clip[i, :] = stretch(clip[i, :])

    # Save new tiff
    #
    #  EDIT: instead of SaveArray, let's break all the
    #  SaveArray steps out more explicity so
    #  we can overwrite the offset of the destination
    #  raster
    #
    ### the old way using SaveArray
    #
    # gdalnumeric.SaveArray(clip, "OUTPUT.tif", format="GTiff", prototype=raster_path)
    #
    ###
    #
    gtiffDriver = gdal.GetDriverByName('GTiff')
    if gtiffDriver is None:
        raise ValueError("Can't find GeoTiff Driver")
        gtiffDriver.CreateCopy("OUTPUT.tif",OpenArray(clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset))

    # Save as an 8-bit jpeg for an easy, quick preview
    clip = clip.astype(gdalnumeric.uint8)
    gdalnumeric.SaveArray(clip, "OUTPUT.jpg", format="JPEG")

    gdal.ErrorReset()


def spi_mask(raster_path, mask_path):


    ds1 = gdal.Open(raster_path)
    gt1 = ds1.GetGeoTransform()    #

    ds2 = gdal.Open(mask_path)
    gt2 = ds2.GetGeoTransform()

    banda = ds1.GetRasterBand(1)
    type_banda = banda.DataType
    type_banda_name = gdal.GetDataTypeName(type_banda)

    rows = ds2.RasterYSize
    cols = ds2.RasterXSize
    # xmin,ymin,xmax,ymax = ds2.GetExtent()

    top_left_x = gt2[0]
    we_pixel_resolution = gt2[1]
    zero_0 = gt2[2]
    top_left_y = gt2[3]
    zero_1 = gt2[4]
    ns_pixel_resolution = gt2[5]  # negative value

    r1 = [gt1[0], gt1[3], gt1[0] + (gt1[1] * ds1.RasterXSize), gt1[3] + (gt1[5] * ds1.RasterYSize)]
    r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * ds2.RasterXSize), gt2[3] + (gt2[5] * ds2.RasterYSize)]
    print r1
    print r2

    intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
    print intersection

    def world2Pixel(geoMatrix, x, y):
        """
        Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
        the pixel location of a geospatial coordinate
        """
        ulX = geoMatrix[0]
        ulY = geoMatrix[3]
        xDist = geoMatrix[1]
        yDist = geoMatrix[5]
        rtnX = geoMatrix[2]
        rtnY = geoMatrix[4]
        pixel = int((x - ulX) / xDist)
        line = int((ulY - y) / xDist)
        return pixel, line

    primo = intersection[0]
    secondo = intersection[1]
    terzo = intersection[2] - intersection[0]
    quarto = intersection[3] - intersection[1]
    quinto = intersection[2] - intersection[0]
    sesto = intersection[3] - intersection[1]


    # Convert the layer extent to image pixel coordinates
    ulX, ulY = world2Pixel(gt2, primo, secondo)
    print ulX, ulY


    # Then convert that rectangle into pixels for each image by subtracting the top and left coordinates and dividing by the pixel size, rounding up.
    # From here you can call ReadRaster() on each image, giving it the pixel extents you've just calculated:

    # band.ReadRaster(px1[0], px1[1], px1[2] - px1[0], px1[3] - px1[1], px1[2] - px1[0], px1[3] - px1[1],
    #             # <band's datatype here>
    # )

    # banda.ReadRaster(primo, secondo, terzo, quarto, quinto, sesto, type_banda)

    # data2 = banda.ReadAsArray(primo, secondo, cols, rows)
    # data2 = banda.ReadAsArray(100,100,50,50)
    # print data2

    # Write the out file
    driver = gdal.GetDriverByName("GTiff")

    nome_tif_spi_mask = "trmm_3B43_17years_monthly/spi_calc/spi_mask.tif"
    print nome_tif_spi_mask


    # raster_spi_mask = driver.Create(nome_tif_spi_mask, cols, rows, 1, type_banda)
    # gdalnumeric.CopyDatasetInfo(ds2, raster_spi_mask)
    # banda_dove_scrivere_raster_spi_mask = raster_spi_mask.GetRasterBand(1)

    # try:
    #     gdalnumeric.BandWriteArray(banda_dove_scrivere_raster_spi_mask, data2)
    #     print "Standard Deviation raster exported in " + nome_tif_spi_mask + "\n"
    #     return raster_spi_mask
    # except IOError as err:
    #     return str(err.message) + "\n"


anno = 2015
base_line = 9814
mese_min = 9
mese_max = 9

spi_frame = (mese_max-mese_min)+1
climatology, current = collect_prec_files_3b43('trmm_3B43_17years_monthly/convertiti/', mese_min, mese_max, anno)

# print climatology
# print current

# mean_climatology = genera_means('trmm_3B43_17years_monthly/convertiti/', climatology, mese_min, mese_max, base_line)
# std_climatology = genera_std('trmm_3B43_17years_monthly/convertiti/', climatology, mese_min, mese_max, mean_climatology, base_line)
# mean_current = genera_means('trmm_3B43_17years_monthly/convertiti/', current, mese_min, mese_max, anno)
# spi_file = spi(mean_current, mean_climatology, std_climatology, mese_min, mese_max, anno,spi_frame)

# mask_file = 'trmm_3B43_17years_monthly/spi_data/ca_countries.shp'
# mask_rast = 'trmm_3B43_17years_monthly/spi_data/masks/ca_mask.tif'
# rast_file = 'trmm_3B43_17years_monthly/spi_calc/spi_3_7_9_2015.tif'

# Troppo Complesso Semplifichiamo con Algebra delle Mappe
# spi_cut_shp(mask_file, rast_file)
# spi_mask(rast_file, mask_rast)


