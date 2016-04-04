# coding=utf-8
import urllib2

url = "http://giovanni.sci.gsfc.nasa.gov/giovanni/#service=ArAvTs&starttime=1999-12-31T00:00:00Z&" \
      "endtime=2015-12-30T23:59:59Z&shape=state_dept_countries/shp_66&" \
      "bbox=24.696775000000116,22.000000000000227,36.249553680000055,31.6709900000003&" \
      "data=TRMM_3B42RT_daily_7_precipitation%28units%3Dinch%2Fday%29"

risposta =  urllib2.urlopen(url)
html = risposta.read()

print html