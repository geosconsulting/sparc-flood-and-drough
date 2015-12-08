"""Graph a histogram of a remotely sensed image"""
import gdalnumeric
import turtle as t
import pandas as pd
from osgeo import gdal, gdalnumeric
import os, sys
gdal.UseExceptions()
import seaborn as sns

# GENERAZIONE HISTOGRAMMA CON TURTLE SCENICO MA ROTTURA

# bins=range(0,256))
def histogram(a, bins=range(0,256)):

  """
  Histogram function for multi-dimensional array.
  a = array
  bins = range of numbers to match 
  """
  fa = a.flat
  n = gdalnumeric.numpy.searchsorted(gdalnumeric.numpy.sort(fa), bins)
  n = gdalnumeric.numpy.concatenate([n, [len(fa)]])
  hist = n[1:]-n[:-1] 
  return hist

def draw_histogram_turtle(hist, scale=True):
    t.color("black")
    # Draw the axes
    axes = ((-355, -200),(355, -200),(-355, -200),(-355, 250))
    t.up()
    for p in axes:
      t.goto(p)
      t.down()
    # Labels
    t.up()
    t.goto(0, -250)
    t.write("VALUE",font=("Arial,",12,"bold"))
    t.up()
    t.goto(-400, 280)
    t.write("FREQUENCY",font=("Arial,",12,"bold"))
    # Tick marks
    # x axis
    x = -355
    y = -200
    t.up()
    for i in range(1,11):
      x = x+65
      t.goto(x,y)
      t.down()
      t.goto(x,y-10)
      t.up()
      t.goto(x,y-25)
      t.write("%s" % (i*25), align="center")
    # y axis
    x = -355
    y = -200
    t.up()
    pixels = sum(hist[0])
    if scale:
      max = 0
      for h in hist:
        hmax = h.max()
        if hmax > max:
          max = hmax
      pixels = max
    label = pixels/10
    for i in range(1,11):
      y = y+45
      t.goto(x,y)
      t.down()
      t.goto(x-10,y)
      t.up()
      t.goto(x-15,y-6)
      t.write("%s" % (i*label), align="right")
    # Plot each histogram as a colored line
    x_ratio = 709.0 / 256
    y_ratio = 450.0 / pixels
    # Add more colors to this list if comparing
    # more than 3 bands or 1 image
    colors = ["red", "green", "blue"]
    for j in range(len(hist)):
      h = hist[j]
      x = -354
      y = -199
      t.up()
      t.goto(x,y)
      t.down()
      t.color(colors[j])
      for i in range(256):
        x = i * x_ratio
        y = h[i] * y_ratio
        x = x - (709/2)
        y = y + -199
        t.goto((x,y))

def draw_histogram_turtle_change_val(hist, scale=False):

    t.color("black")
    # Draw the axes
    axes = ((-35.5, -20.0),(35.5, -20.0),(-35.5, -20.0),(-35.5, 25.0))
    t.up()
    for p in axes:
      t.goto(p)
      t.down()
    # Labels
    t.up()
    t.goto(0, -25.0)
    t.write("VALUE",font=("Arial,",12,"bold"))
    t.up()
    t.goto(-40.0, 28.0)
    t.write("FREQUENCY",font=("Arial,",12,"bold"))
    # Tick marks
    # x axis
    x = -35.5
    y = -20.0
    t.up()
    for i in range(1,11):
      x = x+6.5
      t.goto(x,y)
      t.down()
      t.goto(x,y-1.0)
      t.up()
      t.goto(x,y-2.5)
      t.write("%s" % (i*2.5), align="center")
    # y axis
    x = -35.5
    y = -20.0
    t.up()
    pixels = sum(hist[0])
    if scale:
      max = 0
      for h in hist:
        hmax = h.max()
        if hmax > max:
          max = hmax
      pixels = max
    label = pixels/1.0
    for i in range(1,11):
      y = y+4.5
      t.goto(x,y)
      t.down()
      t.goto(x-1.0,y)
      t.up()
      t.goto(x-1.5,y-.6)
      t.write("%s" % (i*label), align="right")
    # Plot each histogram as a colored line
    x_ratio = 70.90 / 256
    y_ratio = 45.00 / pixels
    # Add more colors to this list if comparing
    # more than 3 bands or 1 image
    colors = ["red"]
    for j in range(len(hist)):
      h = hist[j]
      x = -35.4
      y = -19.9
      t.up()
      t.goto(x,y)
      t.down()
      t.color(colors[j])
      for i in range(256):
        x = i * x_ratio
        y = h[i] * y_ratio
        x = x - (70.9/.2)
        y = y + -19.9
        t.goto((x,y))

# GENERAZIONE HISTOGRAMMA CON TURTLE SCENICO MA ROTTURA

def plotRasterHistogram(file_mean):

    #Open the dataset
    ds1 = gdal.Open(file_mean)
    banda = ds1.GetRasterBand(1)
    dati = gdalnumeric.BandReadAsArray(banda)

im = "calc/historical/mean_sa_2330_11_19792014.tif"
plotRasterHistogram(im)

# GENERAZIONE HISTOGRAMMA CON TURTLE SCENICO MA ROTTURA
# histograms = []
# arr_10_days = gdalnumeric.LoadFile(im)
# for b in arr_10_days:
#     histograms.append(histogram(b))
#
# draw_histogram_turtle_change_val(histograms)
#
# # Hide our pen
# t.pen(shown = False)
# t.done()


