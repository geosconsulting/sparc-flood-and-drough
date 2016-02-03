from ftplib import FTP
import os, zipfile, arcpy, datetime, string,shutil,urllib2
from BeautifulSoup import BeautifulSoup
from datetime import date, timedelta

from arcpy import env


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def connect():
        """
        This function connects to the remote FTP sites and changes the working dir to the
        root depending if it is hdf, bin or grib.
        """
        ftp = FTP(address)
        ftp.login()
        ftp.cwd(remote_folder)
        return ftp

        
def _downloadAll2(tile):
        """
        Handles the download of a single file and write its chunks to a file with the same name
        """

        ftp = connect()
        files = ftp.nlst()
        files = sorted(files)
        #selecting last 30 available days
        lastNdaysAvailable = files[-time_window:]
        #print "lastNdaysAvailable: " + str(lastNdaysAvailable)
        localcount = 0
        #arcpy.AddMessage('Connecting to NASA website')
        #not remove days that we have already in the SDI
        daysAvailableAndNotCollected = []
        for i in lastNdaysAvailable:
                if i[:7] not in days_we_have:
                        print i, "is new"
                        daysAvailableAndNotCollected.append(i)
                else:
                    print i, "is not new"
        #print "daysAvailableAndNotCollected: " + str(daysAvailableAndNotCollected)
        newfiles = []
        #sometimes DFO stop updating the tile. therefore we have to remove from the list the very old days (not in SDI, but older than what we want)
        for i in daysAvailableAndNotCollected:
                if i[:7] >= oldest_yearday:
                    newfiles.append(i)
        print "newfiles: " + str(newfiles)
        #there's a day which is not properly georeferenced
##        badDay = '2011298'
##        for i in newfiles:
##                print i
##                if i[:7] == badDay:
##                        newfiles.remove(i)
                
        for filename in newfiles:
                file = open(os.path.join(tempPath,filename),"wb")
                newfile = os.path.join(tempPath,filename)
                localcount = localcount + 1
                try:
                      ftp.retrbinary("RETR " + filename,file.write)
                except Exception:
                      return newfiles
                mess1 = 'DOWNLOADED %s ' % filename
                mess2  = ' - Zipfile n. %s' % localcount
                mess3 = ' in the tile n. %s' % count
                mess4 = ' (of %s)' % totTiles
                messFin = mess1 + mess2 + mess3 + mess4
                print messFin
                #arcpy.AddMessage('Downloaded %s' % filename)
                file.close()
        return newfiles

def download(url):
        newfiles = []
        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s \n" % (file_name, file_size)

        file_size_dl = 0
        block_sz = int(file_size)/10
        count = 0
        while True:
            count = count + 1
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*count
            print status

        f.close()
        return file_name

def _downloadAll(tile):
        """
        Handles the download of a single file and write its chunks to a file with the same name
        """
        html_page = urllib2.urlopen(remote_folder)
        soup = BeautifulSoup(html_page)
        files = []
        for link in soup.findAll('a'):
            daytilezip = link.get('href')
            files.append(daytilezip)
        #selecting last 30 available days
        lastNdaysAvailable = files[-time_window:]
        #print "lastNdaysAvailable: " + str(lastNdaysAvailable)
        localcount = 0
        #arcpy.AddMessage('Connecting to NASA website')
        #not remove days that we have already in the SDI
        daysAvailableAndNotCollected = []
        for i in lastNdaysAvailable:
                if i[:7] not in days_we_have:
                        print i, "is new"
                        daysAvailableAndNotCollected.append(i)
                else:
                    print i, "is not new"
        #print "daysAvailableAndNotCollected: " + str(daysAvailableAndNotCollected)
        newfiles = []
        #sometimes DFO stop updating the tile. therefore we have to remove from the list the very old days (not in SDI, but older than what we want)
        for i in daysAvailableAndNotCollected:
                if i[:7] >= oldest_yearday:
                    newfiles.append(i)
        print "newfiles: " + str(newfiles)

        for filename in newfiles:
                file = open(os.path.join(tempPath,filename),"wb")
                newfile = os.path.join(tempPath,filename)
                localcount = localcount + 1
                url = remote_folder + filename
                download(url)
                mess1 = 'DOWNLOADED %s ' % filename
                mess2  = ' - Zipfile n. %s' % localcount
                mess3 = ' in the tile n. %s' % count
                mess4 = ' (of %s)' % totTiles
                messFin = mess1 + mess2 + mess3 + mess4
                print messFin
                #arcpy.AddMessage('Downloaded %s' % filename)
                file.close()
        return newfiles

def _unzip(newfiles):
        arcpy.AddMessage('unzipping...')
        #now = str(datetime.datetime.now())[:19]
        listofnewshapes = []
        for zfilename in newfiles:
                try:
                        zip = zipfile.ZipFile(zfilename)
                        zip.extractall(tempPath)
                        listella = zip.namelist()
                        num_of_shp_in_zip = 0
                        for content in listella:
                                if content[-4:] == '.shp':
                                        listofnewshapes.append(content)
                                        num_of_shp_in_zip = 1
                        confirmMessage = zfilename + ' unzipped'
                        if num_of_shp_in_zip == 0:
                                errortype = 'No shapefiles in zip file'
                                rows = arcpy.InsertCursor(errorFile)
                                row = rows.newRow()
                                row.NAME = zfilename
                                row.ERROR_Type = errortype
                                rows.insertRow(row)
                                del row
                                del rows
                                print errortype
                        else:
                                print confirmMessage
                        #print listofnewshapes
                except Exception:
##                        errortype = zfilename + ' was corrupted - skipped during extraction process'
##                        errorMessage = '{0:20} ==> {1:40}'.format(now, errortype)
##                        rows = arcpy.InsertCursor(errorFile)
##                        row = rows.newRow()
##                        row.NAME = zfilename
##                        row.ERROR_Type = 'Error in unzip'
##                        rows.insertRow(row)
##                        del row
##                        del rows
##                        textfile.write(errorMessage)
                        print errortype
##                        textfile.write('\n')
                        pass
        return listofnewshapes



def _process(listofunzippedshapes):
        file_Location = tempPath
        schemaType = "NO_TEST"
        fieldMappings = ""
        subtype = ""
        disslist = []
        print ''
        print "- Processing the flood shapefiles..."
        arcpy.AddMessage('processing the flood shapefiles...')
        print ""

#try:
        # All polygon FCs in the workspace are floods areas shapefiles, we want to append these to the empty FC
        fcList = arcpy.ListFeatureClasses("","POLYGON")
        # except for the possible shapefiles processed previously
        for file1 in fcList:
            if file1[:4] == 'HR_F':
                    fcList.remove(file1)
        # list will resemble ["MSW_2011238_000E010N_2D2O_2C29_V.shp", "MSW_2011239_000E010N_2D2O_2C29_V.shp"]

        # this process creates a dissolved shapefile for each day
        for day in fcList:
                dissname = os.path.join(tempPath, (os.path.splitext(day)[0] + '_diss' + '.shp'))
                if not os.path.exists(dissname):
                        #try:                                        
                        arcpy.Dissolve_management(day, dissname)
                        arcpy.Delete_management(day)
                        confirmMessage = day + ' processed (spatial operations)'
                        arcpy.AddMessage(confirmMessage)
                        disslist.append(dissname)
                        print confirmMessage


        # this process adds a field to each dissolved shapefile and calculate it with correct year and day
        arcpy.AddMessage('Adding fields and calculating them ')
        for shp in disslist:
                arcpy.AddField_management(shp , "year_day", "TEXT", "","", "50")
                posiz = string.find(shp, 'MSW_')
                #sometimes the shapefile starts with 'FMM'
                if posiz < 5:
                        posiz = string.find(shp, 'FMM_')
                posizYearDayA = posiz + 4
                posizYearDayB = posizYearDayA + 7
                yearday = str(shp)[posizYearDayA:posizYearDayB]
                print shp + ' processed (attribute operations)'
                arcpy.CalculateField_management(shp , "year_day", "str('"+yearday+"')", "PYTHON")
        dissClip = []
        for shp in disslist:
            shpClip = shp[:-4] + "_clip.shp"#
            dissClip.append(shpClip)
            print 'Clipping out the ocean from the shapefile ' + shpClip
            sr = arcpy.Describe(shp).spatialReference
            # If the spatial reference is unknown
            if sr.name == "Unknown":
                    arcpy.DefineProjection_management(shp,spatial_reference)
            arcpy.Clip_analysis(shp,admin,shpClip,"#")
        collectingLocal_todiss = collectingLocal[:-4] + "_todiss.shp"
        if not os.path.exists(os.path.join(tempPath,collectingLocal_todiss)): 
            # Process:  Create a new empty feature class to append shapefiles into
            print ''
            print '- Creating local empty collecting file: ' + os.path.join(tempPath,collectingLocal)
            arcpy.CreateFeatureclass_management(tempPath, collectingLocal_todiss, "POLYGON", shp)

        # Process: Append the dissolved feature classes into the empty feature class
        arcpy.AddMessage('Appending the single days shapefile to the collecting shapefile')
        print '- Appending the single days shapefile to the collecting shapefile'
        arcpy.Append_management(dissClip, tempPath + os.sep + collectingLocal_todiss, schemaType, fieldMappings, subtype)

        # Define the output projection
        arcpy.DefineProjection_management(tempPath + os.sep + collectingLocal_todiss,"GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
        print '- Defining projection'
        #dissolving by day
        print "- Dissolving by day"
        collectingLocal_toInters = collectingLocal[:-4] + "_toInters.shp"
        arcpy.Dissolve_management(tempPath + os.sep + collectingLocal_todiss, tempPath + os.sep + collectingLocal_toInters,
                          "year_day", "", "MULTI_PART")
        print '- Intersecting with Admin 0'
        collectingLocal_toReDissolve = collectingLocal[:-4] + "_toReDissolve.shp"
        arcpy.Intersect_analysis ([tempPath + os.sep + collectingLocal_toInters,admin], collectingLocal_toReDissolve, "ALL", "", "")
        print '- Intersected shapefile: ' + collectingLocal_toReDissolve
        print '- Dissolving by Country'
        arcpy.Dissolve_management(collectingLocal_toReDissolve,tempPath + os.sep + collectingLocal,"year_day;ISO3_CODE","#","MULTI_PART","DISSOLVE_LINES")
        #append the results into the SDI
        print '- Appending the processing results into the SDI collecting file'
        #arcpy.Append_management(tempPath + os.sep + collectingLocal,collectingSDI, schemaType, fieldMappings, subtype)
        # Process: delete the temporary dissolved shapefiles
        print '- Deleting all the temporary files...'
        arcpy.AddMessage('Deleting temporary data that you even haven t seen')
        arcpy.Delete_management(tempPath + os.sep + collectingLocal)
        arcpy.Delete_management(collectingLocal_todiss)
        arcpy.Delete_management(collectingLocal_toInters)
        arcpy.Delete_management(collectingLocal_toReDissolve)
        for shp in disslist:
            arcpy.Delete_management(shp)
        for clip in dissClip:
            arcpy.Delete_management(clip)


        #except:
        # If an error occurred while running a tool print the messages
        #print arcpy.GetMessages()
            
def _removeOld():
        days_to_remove = []
        for i in days_we_have:
                if i < oldest_yearday:
                        days_to_remove.append(i)
        if len(days_to_remove) > 0:
            days_in_expressions = str(days_to_remove)[1:-1]
            #when you creates string from lists, you can have some disturbing 'u'
            days_in_expressions = days_in_expressions.replace('u', '')
            days_in_expressions = '(' + days_in_expressions + ')'
            expression = 'YEAR_DAY in ' + days_in_expressions
            arcpy.MakeFeatureLayer_management (collectingSDI, "collecting")
            arcpy.SelectLayerByAttribute_management ("collecting", "NEW_SELECTION", expression)
            count_to_delete = int(arcpy.GetCount_management("collecting").getOutput(0))
            if count_to_delete > 0:
                    print '- Removing ' + str(count_to_delete) + ' features because older than 30 days'
                    arcpy.DeleteFeatures_management("collecting")





tilelist = ['000e010n', '000e020n', '010e000s', '010e010n', '010e010s', '010e020n', \
            '010e020s', '010e030s', '010w010n', '010w020n', '020e000s', '020e010n', '020e010s', \
            '020e020n', '020e020s', '020e030s', '020w010n', '020w020n', '030e000s', '030e010n', \
            '030e010s', '030e020n', '030e020s', '040e010n', '040e010s', '040e020n', '040e020s', \
            '040e030n', '040e040n', '050e020n', '050e030n', '050e040n', '060e030n', '060e040n', \
            '070e010n', '070e020n', '070e030n', '070e040n', '080e010n', '080e020n', '080e030n', \
            '090e010n', '090e020n', '090e030n', '100e000s', '100e010n', '100e020n', '100e030n', \
            '110e000s', '110e010n', '110e030n', '120e000s', '120e010n', '120e020n', '130e000s', \
            '140e000s','080w010n','070w010n','080w000s','080w010s','070w010s','070w020s','080w010s','060w020s']
#tilelist = ['010e020n','000e020n','010w020n','010w010n','020w010n','010e010n','020e010n','000e010n']

tilelist = ['080w010n','080w000s']
totTiles = len(tilelist)


admin = r"C:\Users\andrea.amparore\Desktop\Scheduled_tasks\MODIS_SurfaceWater\BND_ADM0_A_UNGWIG_2012.shp"
collectingSDI = r"C:\Users\andrea.amparore\Desktop\Scheduled_tasks\wfp__hq_esri__appsrv.sde\hq_esri.wfp.NHR\nhr_faa30days_dfo"
collectingSDI = r"C:\Users\andrea.amparore\Desktop\Scheduled_tasks\wfp__hq_esri__directdb__10_11_40_221.sde\hq_esri.wfp.NHR\nhr_faa30days_dfo"



#collectingSDI = r"C:\Users\z400wfp\Desktop\Scheduled_tasks\wfp__hq_esri__appsrv.sde\hq_esri.wfp.NHR\test"
admin = r"C:\Data\Scripts\Scheduled_tasks\MODIS_SurfaceWater\01_Admin\BND_ADM0_GADM_10.shp"
#collectingSDI = r"C:\DATA\Various\00_SDE_Connection_files\wfp__hq_esri__appsrv.sde\hq_esri.wfp.NHR\nhr_faa30days_dfo"
collectingSDI = r"C:\Data\Scripts\Scheduled_tasks\wfp__hq_esri__appsrv.sde\hq_esri.wfp.NHR\nhr_faa30days_dfo"

tempPath = r"C:\TEMP"


time_window = 30


#arcpy.tempPathorkspace = SDIpath
os.chdir(tempPath)
today = datetime.date.today()
hour = str(datetime.datetime.now())[11:13] + str(datetime.datetime.now())[14:16]
todaystr = today.isoformat()
todaystr = todaystr.replace("-", "_")
todaystr = "DF0_working_folder_" + todaystr + "_" + hour
if not os.path.exists(todaystr):
        os.mkdir(todaystr)
tempPath = os.path.join(tempPath,todaystr)

print "New temp folder created: " + tempPath
os.chdir(tempPath)
#templateCollecting = r"C:\TEMP\DF0_working_folder_2014_08_13_1109\nhr_faa30days_dfodiss.shp"
env.workspace = tempPath

nDaysago =date.today()-timedelta(time_window)
oldest_day_of_year = nDaysago.timetuple().tm_yday
oldest_yearday = str(nDaysago.year) + str(oldest_day_of_year)
print "oldest day to download: " + oldest_yearday

listofunzippedshapes = []

collectingLocal = "nhr_faa30days_dfo.shp"

#creates a list of the days already in the SDI
days_we_have = unique_values(collectingSDI, "YEAR_DAY")

print "So far we have " + str(len(days_we_have)) + " days"
#print days_we_have

count = 0
ndownloaded = 0

# for each tile, create the list of missing days and download them (function _downloadAll)
# then unizp them
for tile in tilelist:
        print '\nDOWNLOAD AND PROCESS TILE ' + tile
        address = 'csdms.colorado.edu'
        remote_folder = 'pub/flood_observatory/MODISlance/' + tile + '/'
        remote_folder = 'http://csdms.colorado.edu/pub/flood_observatory/MODISlance/' + tile + '/'
        count = count + 1
        now = datetime.datetime.now()
        print tile, remote_folder
        newfiles = _downloadAll(tile)
        ndownloaded = ndownloaded + len(newfiles)
        message = 'End of dowloading process for the tile n. ' + str(count)
        message2 = str(ndownloaded)  + ' zipfiles downloaded from Modis Lance'
        print message
        print message2
        countzip = len(newfiles)
        unzippedshapes = _unzip(newfiles)
        for i in unzippedshapes:
            listofunzippedshapes.append(i)

print ''
# if there's something new, start the process (attributal, spatial, appending to the localCollecting, dissolving by day, append to the SDI) 
if len(listofunzippedshapes) > 0:
        _process(listofunzippedshapes)
        # and finally remove the old days from the collecting fc in the SDI
        _removeOld()
        print ""
        print 'Mission accomplished, man! Go and check the output!'
        #arcpy.AddMessage('Mission accomplished, man! Go and check the output here: ' + output_location)
else:
    print 'Nothing new available, no actions taken'

