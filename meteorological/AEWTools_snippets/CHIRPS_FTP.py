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
