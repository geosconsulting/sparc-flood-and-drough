import os
import numpy as np
import gdal
from gdalconst import *
from osgeo import osr
from osgeo.gdalconst import GA_ReadOnly
from ftplib import FTP
gdal.UseExceptions()

def FtpConnectionFilesGatheringTRMM(anno, mese,giorno, usr="fabiolana.notizie@gmail.com", pwd="fabiolana.notizie@gmail.com"):

    lista_3B42RT = []

    if len(giorno) < 2:
        giorno = '0' + giorno

    if len(mese) < 2:
        mese = '0' + mese

    if int(anno) < 2014:
        directory = '/sm/705/GIS/' + anno + '/' + mese + '/' + giorno
    else:
        directory = "/sm/705/" + anno + '/' + mese

    try:
        ftp = FTP("arthurhou.pps.eosdis.nasa.gov")
        ftp.login(usr, pwd)
        ftp.cwd(directory)
        msgFTP_arthurhou = str(ftp.getwelcome())
    except Exception as e:
        msgFTP_arthurhou = str(e)

    for file in ftp.nlst():
        filename, file_extension = os.path.splitext(file)
        lista_3B42RT.append(filename)

    ftp.quit()
    ftp.close()

    return msgFTP_arthurhou, lista_3B42RT

def FtpConnectionFilesGatheringTRMM_10Days():


    try:
        ftp = FTP("disc2.nascom.nasa.gov/data/TRMM/Gridded/Derived_Products/3B42_V6/10-day/2006")
        # http://pmm.nasa.gov/data-access/data-sources#GESDISC
        ftp.login()
        msgFTP_10Days = str(ftp.getwelcome())
    except Exception as e:
        msgFTP_10Days = str(e)
        print msgFTP_10Days


    ftp.quit()
    ftp.close()

    return msgFTP_10Days

def FtpConnectionFilesGatheringIMERG(anno, mese, usr="fabio.lana@wfp.org", pwd="fabio.lana@wfp.org"):

    lista_IMERG = []

    if len(mese) < 2:
        mese = '0' + mese

    if int(anno) < 2015:
        code = 0
        msgFTP_jsimpson = 'GPM Data Area available from March 2015 onwards'
    else:
        code = 1
        directory = '/data/imerg/early/' + anno + mese
        try:
            ftp = FTP("jsimpson.pps.eosdis.nasa.gov")
            ftp.login(usr, pwd)
            ftp.cwd(directory)
            msgFTP_jsimpson = str(ftp.getwelcome())
        except Exception as e:
            msgFTP_jsimpson = str(e)

        for file in ftp.nlst():
            filename, file_extension = os.path.splitext(file)
            lista_IMERG.append(filename)

        ftp.quit()
        ftp.close()

    return code, msgFTP_jsimpson, lista_IMERG

def FtpConnectionFilesGatheringGPM(anno, mese, usr="fabio.lana@wfp.org", pwd="fabio.lana@wfp.org"):

    lista_GPM = []

    # if len(mese) < 2:
    #     mese = '0' + mese
    #
    # if int(anno) < 2015:
    #     code = 0
    #     msgFTP_jsimpson = 'GPM Data Area available from March 2015 onwards'
    # else:
    #     code = 1
    #     directory = '/data/imerg/early/' + anno + mese
    #     try:
    #         ftp = FTP("jsimpson.pps.eosdis.nasa.gov")
    #         ftp.login(usr, pwd)
    #         ftp.cwd(directory)
    #         msgFTP_jsimpson = str(ftp.getwelcome())
    #     except Exception as e:
    #         msgFTP_jsimpson = str(e)
    #
    #     for file in ftp.nlst():
    #         filename, file_extension = os.path.splitext(file)
    #         lista_IMERG.append(filename)
    #
    #     ftp.quit()
    #     ftp.close()

    # return code, msgFTP_jsimpson, lista_IMERG
    pass

def FtpConnectionFilesRetrieval(ecmwf_dir,nomefile):

    lista_files_ECMWF = []

    try:
        ftp = FTP('ftp.wfp.org')
        ftp.login('WFP_GISviewer','FTPviewer')
        messaggioServerFTP = str(ftp.getwelcome()) + "\n"
    except:
        pass

    gFile = open(ecmwf_dir + nomefile, "wb")
    ftp.retrbinary("RETR " + nomefile, gFile.write)
    gFile.close()
    ftp.quit

    return messaggioServerFTP, lista_files_ECMWF

# Function to read the original file's projection:
def GetGeoInfo(FileName):

    SourceDS = gdal.Open(FileName, GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataTypeName = gdal.GetDataTypeName(DataType)
    print "Data Type Name : " + str(DataTypeName)

    NunBandsInGRIB = SourceDS.RasterCount

    for numero_banda in range(1, NunBandsInGRIB + 1):
        TPBand = SourceDS.GetRasterBand(numero_banda)
        metadati = TPBand.GetMetadata()
        if(metadati['GRIB_ELEMENT'] == 'TP'):
            print metadati
            DataTypeTPInt = TPBand.DataType
            DataTypeTP = gdal.GetDataTypeName(DataTypeTPInt)
            DataTP = TPBand.ReadAsArray()
            # stats = TPBand.GetStatistics(True, True)
            # if stats is None:
            #     pass
            # print "Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
            # print "NO DATA VALUE = ", TPBand.GetNoDataValue()
            # print "MIN = ", TPBand.GetMinimum()
            # print "MAX = ", TPBand.GetMaximum()
            # print "SCALE = ", TPBand.GetScale()
            # print "UNIT TYPE = ", TPBand.GetUnitType()
            break

    return NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt

# Function to write a new file.
def CreateGeoTiffFromSelectedBand(Name, Array, driver, NDV, xsize, ysize, GeoT, Projection, DataType):

    if DataType == 'Float32':
        DataType = gdal.GDT_Float32
    elif DataType == 'Float64':
        DataType == gdal.GDT_Float64

    NewFileName = Name + '.tif'
    # Set nans to the original No Data Value
    Array[np.isnan(Array)] = NDV
    # Set up the dataset
    DataSet = driver.Create(NewFileName, xsize, ysize, 1, DataType)  # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())
    # Write the array
    DataSet.GetRasterBand(1).WriteArray(Array)
    if NDV:
        DataSet.GetRasterBand(1).SetNoDataValue(NDV)
    else:
        print "No Data None"

    return NewFileName

def EstrazioneBandaTP_hres(FileName, name_TP_tif_file):

    # FileName = "ecmwf_ftp_wfp/A1D12020000121200001.grib"
    # name_TP_tif_file = "ecmwf_ftp_wfp/TP_0212_2"

    DataSet = gdal.Open(FileName, GA_ReadOnly)
    # Get the first (and only) band.
    Band = DataSet.GetRasterBand(1)
    # Open as an array.
    Array = Band.ReadAsArray()
    # Get the No Data Value
    NDV = Band.GetNoDataValue()
    # Convert No Data Points to nans
    # Array[Array == NDV] = np.nan
    # Now I do some processing on Array, it's pretty complex
    # but for this example I'll just add 20 to each pixel.
    # NewArray = Array + 20  # If only it were that easy
    # Now I'm ready to save the new file, in the meantime I have
    # closed the original, so I reopen it to get the projection
    # information...
    NDV, xsize, ysize, GeoT, Projection, DataType, DataTypeTP, TPBand, DataTP, DataTypeTPInt = GetGeoInfo(FileName)
    # print NDV, xsize, ysize, GeoT, Projection, DataType , DataTypeTPInt
    # print DataTypeTP
    # print DataTP
    # Set up the GTiff driver
    driver = gdal.GetDriverByName('GTiff')

    CreateGeoTiffFromSelectedBand(name_TP_tif_file, DataTP, driver, NDV, xsize, ysize, GeoT, Projection, DataTypeTPInt)

# FtpConnectionFilesGatheringTRMM_10Days()
# EstrazioneBandaTP_hres("ecmwf_ftp_wfp/1209/A1D12090000121900001.grib","ecmwf_ftp_wfp/TP_1209")