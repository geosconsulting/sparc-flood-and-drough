import numpy as np

def bin_convert_asc(BinaryFile):

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

    trmm_file = (np.fromfile(BinaryFile, dtype=np.float32, count=480*1444).byteswap()).reshape((480, 1440))

    ascii_file = open(FileASC, 'w')
    header0 = 'ncols 1440'
    header1 = 'nrows 480'
    header2 = 'xllcorner 0'
    header3 = 'yllcorner -60'
    header4 = 'cellsize 0.25'
    header5 = 'NODATA_value -99999.00'

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

BIN_file = "Flood_byStor_2015112300.bin"
bin_convert_asc(BIN_file)
