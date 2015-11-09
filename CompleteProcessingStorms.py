# -*- coding: utf-8 -*
import dbf
from osgeo import ogr
ogr.UseExceptions()
import psycopg2
import psycopg2.extras
import arcpy
arcpy.CheckOutExtension("spatial")
from arcpy import env
env.overwriteOutput = "true"
import os
import glob
import pycountry
import unittest

class ProjectStorms(object):

    def __init__(self, paese , dbname='geonode-imports', user='geonode', password='geonode'):

        self.proj_dir = "c:/sparc/projects/cyclones"
        self.paese = paese
        self.shape_countries = "c:/sparc/input_data/gaul/gaul_wfp_iso.shp"
        self.campo_nome_paese = "ADM0_NAME"
        self.campo_iso_paese = "ADM0_CODE"
        self.campo_nome_admin1 = "ADM1_NAME"
        self.campo_iso_admin1 = "ADM1_CODE"
        self.campo_nome_admin = "ADM2_NAME"
        self.campo_iso_admin = "ADM2_CODE"

        self.DRIVER = ogr.GetDriverByName("ESRI Shapefile")

        self.schema = 'public'
        self.dbname = dbname
        self.user = user
        self.password = password

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()
        self.storm_winds_tifs_dir = "C:/sparc/input_data/gar_cyc_15_rcl/"
        os.chdir(self.storm_winds_tifs_dir)
        self.storms_annual_tifs = glob.glob("*.tif")

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()

        comando = "SELECT c.name,c.iso2,c.iso3,a.area_name FROM SPARC_wfp_countries c " \
                  "INNER JOIN SPARC_wfp_areas a " \
                  "ON c.wfp_area = a.area_id WHERE c.name = '" + paese + "';"

        self.cur.execute(comando)
        for row in self.cur:
            self.wfp_area = str(row[3]).strip()
            self.iso3 = row[2]
            print self.wfp_area,self.iso3

        if os.path.isfile("C:/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "13.tif"):
            self.population_raster = "C:/sparc/input_data/population/" + self.wfp_area + "/" + self.iso3 + "-POP/" + self.iso3 + "13.tif" #popmap10.tif"
        else:
            print "No Population Raster......"
            self.population_raster = "None"

        self.storms_tifs_dir = "C:/sparc/input_data/gar_cyc_15_rcl"

        os.chdir(self.storms_tifs_dir)
        self.storms_tifs = glob.glob("*.tif")


    def rasterstats_statistics(self,admin_vect_file):

        from rasterstats import zonal_stats
        stats = zonal_stats(admin_vect_file, self.population_raster)
        print stats

        return "Calcoli statistici effettuati per categorie cicloni e popolazione....\n"

    def cut_rasters_storms(self, paese, admin_name, adm_code, adm2_vector):

        #CUT and SAVE Population and Drought Month/Season for each admin2 area
        if self.population_raster != "None":
            self.lscan_cut_adm2 = self.proj_dir + "/" + paese + "/" + admin_name + "_" + adm_code + "/" + adm_code + "_pop.tif"
            try:
                arcpy.gp.ExtractByMask_sa(self.population_raster, adm2_vector.name, adm_code)
                for raster in self.storms_tifs:
                    storm_adm2_out = self.proj_dir + "/" + paese + "/" + admin_name + "_" + adm_code + "/" + adm_code + "_" + raster.split('_')[1]
                    try:
                        print storm_adm2_out
                        # print raster, paese, admin_name, adm_code, adm2_vector.name
                        arcpy.gp.ExtractByMask_sa(arcpy.Raster(self.population_raster), adm2_vector.name, storm_adm2_out)
                    except IOError as errore:
                        print "No Storm Raster"
            except:
                print "No Population Raster"
            self.statistics_storm_zones()

            # self.lscan_cut_adm2 = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + "_pop.tif"
            # try:
            #     arcpy.gp.ExtractByMask_sa(self.population_raster, admin_vect, self.lscan_cut_adm2)
            #     contatore = 1
            #     for raster in self.drought_monthly_tifs:
            #         rst_file = self.drought_monthly_tifs_dir + raster
            #         try:
            #             drought_out = self.proj_dir + paese + "/" + name_admin + "_" + str(code) + "/" + name_admin + "_drmo" + str(contatore) + ".tif"
            #             self.adm2_drought_months.append(drought_out)
            #             arcpy.gp.ExtractByMask_sa(arcpy.Raster(rst_file), admin_vect, drought_out )
            #             contatore += 1
            #         except:
            #             return "No Drought Raster"



    def storm_adm2_polygons(self):

        direttorio = self.proj_dir + "\\" + self.paese
        iso_paese = pycountry.countries.get(name=self.paese).alpha3

        lista = []
        for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
            if direttorio_principale != direttorio:
                try:
                    splittato = direttorio_principale.split("\\")[2]
                    name_adm = splittato.split("_")[0]
                    code_adm = splittato.split("_")[1]
                    files_shp = glob.glob(direttorio_principale + "/*.shp")
                    for file in files_shp:
                        fileName, fileExtension = os.path.splitext(file)
                        try:
                            if str(fileExtension) == '.shp':
                                if '_cy' not in fileName:
                                    shapefile_adm2 = self.DRIVER.Open(file)
                                    layer_admin = shapefile_adm2.GetLayer()
                                    layer_adminProj = layer_admin.GetSpatialRef()
                                    # layer_admin.SetAttributeFilter("ADM2_CODE=" + code_adm)
                                    # calcolo.rasterstats_statistics(file)
                                    calcolo.cut_rasters_storms(self.paese, name_adm, code_adm,shapefile_adm2)
                        except:
                            pass
                except IOError.message as problema_file:
                    print problema_file
        return lista

paese_ricerca = "Philippines"
calcolo = ProjectStorms(paese_ricerca)
calcolo.storm_adm2_polygons()

