# basic NOMADS OpenDAP extraction and plotting script
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import netCDF4

# set up the figure
plt.figure()

# set up the URL to access the data server.
# See the NWW3 directory on NOMADS
# for the list of available model run dates.

mydate = '20160421'
# url='http://nomads.ncep.noaa.gov:9090/dods/wave/nww3/nww3' + mydate + '/nww3' + mydate + '_00z'

#http://nomads.ncep.noaa.gov:9090/dods/gfs_1p00/gfs20160421/gfs_1p00_00z.info
url='http://nomads.ncep.noaa.gov:9090/dods/gfs_1p00/gfs' + mydate + '/gfs_1p00_00z'

# Extract the significant wave height of combined wind waves and swell

file = netCDF4.Dataset(url)
lat  = file.variables['lat'][:]
lon  = file.variables['lon'][:]
#Wave
# data = file.variables['htsgwsfc'][1,:,:]
# descrizione = "surface total precipitation [kg/m^2"
# data = file.variables['apcpsfc'][1,:,:]
descrizione = "0-0.1 m below ground volumetric soil moisture content [fraction]"
data = file.variables['soilw0_10cm'][1, :, :]
file.close()

# Since Python is object oriented, you can explore the contents of the NOMADS
# data set by examining the file object, such as file.variables.

# The indexing into the data set used by netCDF4 is standard python indexing.
# In this case we want the first forecast step, but note that the first time
# step in the RTOFS OpenDAP link is all NaN values.  So we start with the
# second timestep

# Plot the field using Basemap.  Start with setting the map
# projection using the limits of the lat/lon data itself:

m=Basemap(projection='mill',lat_ts=10,llcrnrlon=lon.min(), \
  urcrnrlon=lon.max(),llcrnrlat=lat.min(),urcrnrlat=lat.max(), \
  resolution='c')

# convert the lat/lon values to x/y projections.

x, y = m(*np.meshgrid(lon,lat))

# plot the field using the fast pcolormesh routine
# set the colormap to jet.

m.pcolormesh(x,y,data,shading='flat',cmap=plt.cm.jet)
m.colorbar(location='right')

# Add a coastline and axis values.

m.drawcoastlines()
# Senno mi copre le precipitazioni sui continenti
# m.fillcontinents()
m.drawmapboundary()
m.drawparallels(np.arange(-90., 120.,30.),labels=[1,0,0,0])
m.drawmeridians(np.arange(-180., 180.,60.),labels=[0,0,0,1])

# Add a colorbar and title, and then show the plot.

plt.title(descrizione)
plt.show()