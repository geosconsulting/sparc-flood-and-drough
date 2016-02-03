import os
import numpy as np
import gdal
import matplotlib
import matplotlib.pyplot as plt
from ftplib import FTP
gdal.UseExceptions()
driver = gdal.GetDriverByName('GTiff')
# import gpm

from struct import unpack

try:
  import h5py
except ImportError:
  print 'please install the h5py module so that you will have HDF5 access in python'

def readGrid(fileName,varName,grid):

    print 'readGrid: ' + fileName
    fileHandle = h5py.File( fileName, 'r')
    varExists = varName in fileHandle
    if varExists==False :
        print 'Error: requested variable does not exist in file'
        print '  ', fileName
        print '  ', varName
        return

    grid['data'] = fileHandle[varName]

    return grid['data']

def plotGrid(data, titolo):

    data_flip = np.fliplr(data)
    data = np.transpose(data_flip)

    norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)
    data_no_nan = data[np.logical_not(np.isnan(data))]
    color = np.log10(data)

    # --- generate image and colorbar
    image = plt.imshow(color, interpolation='nearest', norm=norm)

    # --- add labels and color bar
    plt.xlabel('E. Longitude'); plt.ylabel('N. Latitude')
    title = grid['data'].file.filename
    plt.title(titolo)
    barHandle = plt.colorbar(image, norm=norm)
    barHandle.set_label('log10( mm/hour )')
    plt.show()

def list_node(name, obj) :

    global GLOBALoutputFile

    if GLOBALoutputFile != None :
        outputTextFile = open( GLOBALoutputFile, 'a' )

    # --- for all datasets (not groups or files) print info
    if isinstance(obj, h5py.Dataset):
        if GLOBALoutputFile == None :
            print '/' + name, '  ',  obj.dtype, obj.shape
        else:
            aString = str('/' + name + '  ' + str(obj.dtype) + str(obj.shape))
        outputTextFile.write(aString + '\n' )

    # --- if this is a group object with a GridHeader annotation
    if 'GridHeader' in obj.attrs :
        gridHeader = obj.attrs['GridHeader']
        if GLOBALoutputFile == None :
            print obj.name + ' GridHeader attribute:'
            print gridHeader
        else:
            outputTextFile.write(obj.name + ' GridHeader attribute:\n')
            outputTextFile.write(gridHeader + '\n')
    #
    if GLOBALoutputFile != None:
        outputTextFile.close()

def list_contents(fileName, outputFile=None):

    print 'list_contents: ' + fileName
    global GLOBALoutputFile

    GLOBALoutputFile = outputFile

    if GLOBALoutputFile != None :
        print 'writing output to ', GLOBALoutputFile
        outputTextFile = open(GLOBALoutputFile, 'w')
        outputTextFile.write('file: ' + fileName +'\n\n')
        outputTextFile.close()

    fileHandle = h5py.File(fileName, 'r')
    fileHandle.visititems(list_node)

def trmm_convert_txt(BinaryFile):


    BinaryFileNoExtension = BinaryFile.split(".bin")[0]
    FileASC = BinaryFileNoExtension + ".txt"

    f = open(BinaryFile, "rb")
    fOut = open(FileASC, 'w')

    NumbytesFile = 576000
    NumElementxRecord = -1440

    for PositionByte in range(NumbytesFile, 0, NumElementxRecord):

            Record = ''
            for c in range(PositionByte - 720, PositionByte, 1):
                    f.seek(c * 4)
                    DataElement = unpack('>f', f.read(4))
                    Record = Record  + str("%.2f" % DataElement + ' ')

            for c in range(PositionByte - 1440, PositionByte - 720, 1):
                    f.seek(c * 4)
                    DataElement = unpack('>f', f.read(4))
                    Record = Record  + str("%.2f" % DataElement + ' ')

            fOut.write(Record[:-1] + '\n')

    f.close()
    fOut.close()

def trmm_convert_asc(BinaryFile):


    BinaryFileNoExtension = BinaryFile.split(".bin")[0]
    FileASC = BinaryFileNoExtension + ".asc"
    ProjASCFile = BinaryFileNoExtension + ".prj"

    proj_file = open(ProjASCFile, 'w')
    proj_file_header = 'Projection    GEOGRAPHIC\n'
    proj_file_header += 'Datum         WGS84\n'
    proj_file_header += 'Spheroid      WGS84\n'
    proj_file_header += 'Units         DD\n'
    proj_file_header += 'Zunits        NO\n'
    proj_file_header += 'Parameters\n'
    proj_file.write(proj_file_header)

    # trmm_file = np.open(BinaryFile, "rb")
    trmm_file = (np.fromfile(TRMM_file, dtype=np.float32, count=480*1444).byteswap()).reshape((480, 1440))

    ascii_file = open(FileASC, 'w')
    header0='ncols 1440';
    header1='nrows 480';
    header2='xllcorner 0';
    header3='yllcorner -60';
    header4='cellsize 0.25';
    header5='NODATA_value -99999.00';

    ascii_file.write(header0 + "\n")
    ascii_file.write(header1 + "\n")
    ascii_file.write(header2 + "\n")
    ascii_file.write(header3 + "\n")
    ascii_file.write(header4 + "\n")
    ascii_file.write(header5 + "\n")

    formato = "{0} "

    for i in range(0, 480):
        for j in range(0, 1440):
            ascii_file.write(formato.format(trmm_file[i, j]))
        ascii_file.write("\n")
    ascii_file.close()


# imergFile = 'down_nasa_ftp/3B-HHR-E.MS.MRG.3IMERG.20151210-S043000-E045959.0270.V03E.RT-H5'
# TRMM_file = "3B42RT_10day/3B42RT_10day.2015.11.20.bin"

# bin_convert_asc(TRMM_file)
# print bin_convert_asc(TRMM_file)
# titolo = imergFile.split('.')[-4]

# grid = {'data': -9, 'latRange': -9, 'lonRange': -9}
# data = readGrid(imergFile, '/Grid/precipitationCal', grid)
#
# print data.shape

# Another common operation that researchers perform on data read from GPM HDF5 files is to see
# what fraction of a variable exceeds a particular threshold. For example what
# fraction of observations were determined to have
# had heavy rain of 10 millimeters an hour.

# print 'fraction of elements greater than or equal to 10 %f' % float(1.0 * np.sum(np.greater_equal(data, 10))/np.size(data))
# plotGrid(data, titolo)
# list_contents(imergFile, titolo + '.txt')

# gpm.testRun()
