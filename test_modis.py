#!/usr/bin/env python

import ftplib
import numpy as np

ftp = ftplib.FTP("e4ftl01.cr.usgs.gov")

ftp.cwd('MODIS_Composites/MOTA/MCD15A2.005')
data = []
ftp.dir(data.append)
print data[:10]