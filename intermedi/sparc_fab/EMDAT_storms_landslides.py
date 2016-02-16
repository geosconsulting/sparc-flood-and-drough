__author__ = 'fabio.lana'
from urllib2 import Request, urlopen
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData
import csv
import os
import pycountry
import psycopg2
from geopy.geocoders import Nominatim
from geopy.geocoders import GeoNames
import shapefile
import matplotlib.pylab as plt
import matplotlib
matplotlib.style.use('ggplot')
from shapely.geometry import Point, box
from osgeo import ogr

ogr.UseExceptions()

class ScrapingEMDAT(object):

    def __init__(self, iso, hazard):
        self.stringa_richiesta_gar = 'http://www.preventionweb.net/english/hyogo/gar/2015/en/home/data.php?iso=SLV'
        self.stringa_richiesta = 'http://www.emdat.be/disaster_list/php/search.php?continent=&region=&iso=' + iso + '&from=1900&to=2015&group=&type=' + hazard
        self.engine = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
        self.connection = self.engine.connect()
        self.schema_emdat = 'em_dat'
        self.metadata = MetaData(self.engine,schema=self.schema_emdat)
        self.table_name = hazard + "_" + iso

    def scrape_EMDAT(self):

        richiesta = Request(self.stringa_richiesta)
        risposta = urlopen(richiesta)
        ritornati = json.loads(risposta.read(), encoding='LATIN-1')

        return ritornati

    def scrape_GAR(self):

        richiesta_GAR = Request(self.stringa_richiesta_gar)
        risposta_GAR = urlopen(richiesta_GAR)
        ritornato_raw = risposta_GAR.read()

        # ritornati_GAR = json.loads(risposta_GAR.read(), encoding='LATIN-1')
        #
        # return ritornati_GAR

    def write_in_db(self, df_danni):

        try:
            df_danni.to_sql(self.table_name, self.engine,schema= "em_dat")
            self.connection.close()
        except Exception as tabella_esiste:
            print tabella_esiste.message

    def read_from_db(self):

        try:
            df_da_sql = pd.read_sql_table(self.table_name, self.engine, index_col='disaster_no', schema= "em_dat")
            self.connection.close()
            return df_da_sql
        except Exception as tabella_non_esiste:
            print tabella_non_esiste.message

class GeocodeEMDAT(object):

    def __init__(self, paese, hazard):
        self.paese = paese
        self.hazard = hazard
        self.geolocator = Nominatim()
        self.geolocator_geonames = GeoNames(country_bias = self.paese, username='fabiolana', timeout=1)

        self.dir_out = "C:/sparc/input_data/geocoded/new_geocoded_EMDAT/"
        self.gaul_shp = "C:/sparc/input_data/gaul/gaul_wfp_iso.shp"
        self.gaul_dir = "C:/sparc/input_data/gaul/"
        self.totali = 0
        self.successo = 0
        self.insuccesso = 0
        self.gaul_file = None
        self.poligono_controllo = []
        self.n = 0


    def geolocate_accidents(self, luoghi_incidenti):

        geocoding_testo = open(self.dir_out + "/" + self.paese + self.hazard + ".txt", "wb+")
        geocoding_testo_fail = open(self.dir_out + "/" + self.paese + self.hazard + "_fail.txt", "wb+")

        geocoding_testo.write("id,lat,lon,em_dat\n")
        geocoding_testo_fail.write("id,lat,lon,em_dat\n")

        for luogo_incidente in luoghi_incidenti.iteritems():
            try:
                luogo_attivo = luogo_incidente[1]
                if luogo_attivo is not None:
                    print ("Geocoding " + luogo_attivo)
                    location_geocoded = self.geolocator.geocode(luogo_attivo, timeout=30)
                    codice_temp = str(luogo_incidente[0]).split('-')
                    codice = codice_temp[0] + "-" + codice_temp[1]
                    if location_geocoded:
                        scrittura = luogo_attivo + "," + str(location_geocoded.longitude) + "," + str(location_geocoded.latitude) + "," + codice + "\n"
                        print scrittura
                        geocoding_testo.write(scrittura)
                        self.totali += 1
                        self.successo += 1
                    else:
                        geocoding_testo_fail.write(luogo_attivo + "," + str(0) + "," + str(0) + "," + codice + "\n")
                        self.totali += 1
                        self.insuccesso += 1
            except ValueError as e:
                print e.message
        print "Total of %s events with %s successful %s unsuccessful and %d NULL" % (
        str(self.totali), str(self.successo), str(self.insuccesso), (self.totali - self.successo - self.insuccesso))

    def extract_country_shp(self):

            # Get the input Layer
            inShapefile = "C:/sparc/input_data/gaul/gaul_wfp_iso.shp"

            inDriver = ogr.GetDriverByName("ESRI Shapefile")
            inDataSource = inDriver.Open(inShapefile, 0)
            inLayer = inDataSource.GetLayer()
            #print "ADM0_NAME = '" + self.paese + "'"
            inLayer.SetAttributeFilter("ADM0_NAME = '" + str(self.paese) + "'")
            # Create the output LayerS
            outShapefile = "C:/sparc/input_data/countries/" + str(self.paese) + ".shp"
            outDriver = ogr.GetDriverByName("ESRI Shapefile")

            # Remove output shapefile if it already exists
            if os.path.exists(outShapefile):
                outDriver.DeleteDataSource(outShapefile)

            # Create the output shapefile
            outDataSource = outDriver.CreateDataSource(outShapefile)
            out_lyr_name = os.path.splitext(os.path.split(outShapefile)[1])[0]
            outLayer = outDataSource.CreateLayer(out_lyr_name, geom_type=ogr.wkbMultiPolygon)

            # Add input Layer Fields to the output Layer if it is the one we want
            inLayerDefn = inLayer.GetLayerDefn()
            for i in range(0, inLayerDefn.GetFieldCount()):
                fieldDefn = inLayerDefn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()
                #print fieldName
                outLayer.CreateField(fieldDefn)

            # Get the output Layer's Feature Definition
            outLayerDefn = outLayer.GetLayerDefn()
            # Add features to the ouput Layer
            for inFeature in inLayer:
                # Create output Feature
                outFeature = ogr.Feature(outLayerDefn)

                # Add field values from input Layer
                for i in range(0, outLayerDefn.GetFieldCount()):
                    fieldDefn = outLayerDefn.GetFieldDefn(i)
                    fieldName = fieldDefn.GetName()
                    outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),inFeature.GetField(i))

                # Set geometry as centroid
                geom = inFeature.GetGeometryRef()
                outFeature.SetGeometry(geom.Clone())
                # Add new feature to output Layer
                outLayer.CreateFeature(outFeature)

            # Close DataSources
            inDataSource.Destroy()
            outDataSource.Destroy()

    def calc_poligono_controllo(self):

        coords_file_in = self.dir_out + "/" + self.paese + self.hazard + ".txt"
        coords_file_out = self.dir_out + "/" + str(self.paese) + self.hazard + '.csv'

        dentro = 0
        fuori = 0

        if os.path.exists("C:/sparc/input_data/countries/" + self.paese + ".shp"):
            print "File controllo trovato in" + str("C:/sparc/input_data/countries/" + self.paese + ".shp")
            sf = shapefile.Reader("C:/sparc/input_data/countries/" + self.paese + ".shp")
        else:
            print "Devo estrarre"
            self.extract_country_shp()
            sf = shapefile.Reader("C:/sparc/input_data/countries/" + self.paese + ".shp")

        bbox = sf.bbox
        minx, miny, maxx, maxy = [x for x in bbox]

        bounding_box = box(minx, miny, maxx, maxy)
        with open(coords_file_in) as csvfile_in:
            lettore_comma = csv.reader(csvfile_in, delimiter=",", quotechar='"')
            next(lettore_comma)
            with open(coords_file_out, 'wb') as csvfile_out:
                scrittore = csv.writer(csvfile_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                intestazioni = "id", "lat", "lon","emdat"
                scrittore.writerow(intestazioni)
                for row in lettore_comma:
                    punto_corrente = Point(float(row[1]), float(row[2]))
                    print punto_corrente
                    if bounding_box.contains(punto_corrente):
                        stringa = str(row[0]), str(row[1]), str(row[2]), str(row[3])
                        scrittore.writerow(stringa)
                        dentro += 1
                    else:
                        fuori += 1
            csvfile_out.close()
        csvfile_in.close()
        return dentro, fuori

class CreateGeocodedShp(object):

    def __init__(self, paese, hazard):
        self.paese = paese
        self.hazard = hazard
        self.dir_out = "C:/sparc/input_data/geocoded/new_geocoded_EMDAT/"
        self.outDriver = ogr.GetDriverByName("ESRI Shapefile")
        self.outShp = "C:/sparc/input_data/geocoded/new_geocoded_EMDAT/" + self.paese + self.hazard + ".shp"


    def creazione_file_shp(self):

        print("Lo scrivo in %s" % str(self.outShp))
        # Remove output shapefile if it already exists
        if os.path.exists(self.outShp):
            self.outDriver.DeleteDataSource(self.outShp)

        #Set up blank lists for data
        x, y, nomeloc, emdat= [], [], [], []

        print self.dir_out + '/' + self.paese + self.hazard + '.csv'
        with open(self.dir_out + '/' + self.paese + self.hazard + '.csv', 'rb') as csvfile:
            r = csv.reader(csvfile, delimiter=';')
            for i, row in enumerate(r):
                if i > 0: #skip header
                    divisa = row[0].split(",")
                    #print divisa[0]
                    nomeloc.append(divisa[0])
                    x.append(float(divisa[1]))
                    y.append(float(divisa[2]))
                    emdat.append(str(divisa[3]))
                    #date.append(''.join(row[1].split('-')))#formats the date correctly
                    #target.append(row[2])

        #Set up shapefile writer and create empty fields
        w = shapefile.Writer(shapefile.POINT)
        w.autoBalance = 1 #ensures gemoetry and attributes match
        w.field('ID','N')
        w.field('location','C', 50)
        w.field('emdat','C',10)
        # w.field('Target','C',50)
        # w.field('ID','N')

        #loop through the data and write the shapefile
        for j,k in enumerate(x):
            w.point(k,y[j]) #write the geometry
            w.record(k, nomeloc[j], emdat[j]) #write the attributes

        #Save shapefile
        if len(w._shapes)> 0:
            w.save(self.outShp)
        else:
            None

class ManagePostgresDBEMDAT(object):

    def __init__(self):
        self.schema = 'public'
        self.dbname = "geonode-imports"
        self.user = "geonode"
        self.password = "geonode"

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()


    def all_country_db(self):

        comando = "SELECT DISTINCT adm0_name FROM sparc_gaul_wfp_iso;"

        try:
            self.cur.execute(comando)
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            print descrizione_errore, codice_errore
            return codice_errore

        paesi = []
        for paese in self.cur:
            paesi.append(paese[0])
        return sorted(paesi)

    def all_isos_db(self):

        comando = "SELECT DISTINCT iso3 FROM sparc_gaul_wfp_iso;"

        try:
            self.cur.execute(comando)
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            print descrizione_errore, codice_errore
            return codice_errore

        isos = []
        for iso in self.cur:
            isos.append(iso[0])
        return sorted(isos)

class DataAnalysisHistoricalEMDAT(object):

    def __init__(self, df):
        self.df = df

    def plottaggi(self,hazard):

        self.df['inizio'] = pd.to_datetime(self.df['start_date'])
        self.df['anno_inizio'] = pd.DatetimeIndex(self.df['inizio']).year
        self.df['mese_inizio'] = pd.DatetimeIndex(self.df['inizio']).month
        self.df['fine'] = pd.to_datetime(self.df['end_date'])
        self.df['anno_fine'] = pd.DatetimeIndex(self.df['fine']).year
        self.df['mese_fine'] = pd.DatetimeIndex(self.df['fine']).month
        self.df['durata'] = abs(self.df['fine'] - self.df['inizio'])
        self.df['days'] = self.df['durata'] / np.timedelta64(1, 'D')

        data_minima = min(self.df['inizio'])
        data_massima = max(self.df['inizio'])

        self.df['total_affected'] = self.df['total_affected'].astype(int)
        quanti_affected_per_mese = df_valori_letti.groupby('mese_inizio')['total_affected'].sum()
        quanti_affected_per_mese.plot(kind='bar', title = 'People Affected by Month ' + str(paese.name) + " between " + str(data_minima.year) + " and " + str(data_massima.year), x="Million")
        plt.show()

        quanti_per_mese = df_valori_letti.groupby('mese_inizio')['index'].count()
        #print quanti_per_mese

        quanti_per_mese.plot(grid=True,kind='bar',title = 'Frequency of Events by Month ' + str(paese.name) + " between " + str(data_minima.year) + " and " + str(data_massima.year), table=False)
        plt.show()

        df_duration_more_than_1_day = self.df[self.df['days'] > 0]
        df_duration_more_than_1_day_grp_year = df_duration_more_than_1_day.groupby([df_duration_more_than_1_day.index,'anno_inizio']).days.sum()
        df_duration_more_than_1_day_grp_year.plot(kind='bar', title = 'Summed Days of ' + hazard + ' by Year ' +
                                                                      str(paese.name) + " between " + str(data_minima.year) + " and "
                                                                      + str(data_massima.year), x="Days")
        plt.xticks(rotation=20)
        plt.show()

# paese = pycountry.countries.get(name = 'Korea Dem P Rep')

oggetto_isos = ManagePostgresDBEMDAT()
lista_isos = oggetto_isos.all_isos_db()

# for iso in lista_isos:
#     try:
#         paese = pycountry.countries.get(alpha3=iso)
#         iso = paese.alpha3
#         nome_paese = paese.name
#         print nome_paese
#
#         #Fase WebScraping
#         scrapiamo = ScrapingEMDAT(iso, 'Landslide')
#         emdat_paese = scrapiamo.scrape_EMDAT()
#         df_emdat_paese = pd.DataFrame(emdat_paese['data'])
#         scrapiamo.write_in_db(df_emdat_paese)
#         df_valori_letti = scrapiamo.read_from_db()
#
#         df_emdat_paese_divisi = df_valori_letti['location']
#         df_emdat_paese_divisi.name = "locations of accidents"
#         df_emdat_paese_divisi = df_emdat_paese_divisi.dropna(axis=0, how='any')
#
#         locazioni_singole = df_emdat_paese_divisi.str.split(",").apply(pd.Series, 1).stack()
#         locazioni_singole.index = locazioni_singole.index.droplevel(-1)
#         locazioni_singole.to_csv("df_emdat_" + str(paese.name) + "_splittati.csv")
#
#         # Fase Analisi e Visual Interpretation
#         visual_interpretation = DataAnalysisHistoricalEMDAT(df_valori_letti)
#         visual_interpretation.plottaggi(nome_paese)
#
#     except:
#         pass

scrapiamo = ScrapingEMDAT('LBN', 'Landslide')
emdat_paese = scrapiamo.scrape_EMDAT()
df_emdat_paese = pd.DataFrame(emdat_paese['data'])
scrapiamo.write_in_db(df_emdat_paese)

# gar_paese = scrapiamo.scrape_GAR()



# FASE GEOCODING
# locazioni_da_inviare_alla_geocodifica = {}
# indice_esterno = 1
# for indice, locazione in locazioni_singole.iteritems():
#     if locazione is not None and len(locazione)> 0:
#         chiave = str(indice) + "-" + str(indice_esterno)
#         if ';' not in locazione:
#             locazioni_da_inviare_alla_geocodifica[chiave] = str(locazione).strip()
#             indice_esterno += 1
#         else:
#              locazione_annidata = locazione.split(";")
#              for indice_annidato in range(0, len(locazione_annidata)):
#                 locazioni_da_inviare_alla_geocodifica[chiave] = str(locazione_annidata[indice_annidato]).strip()
#                 indice_esterno += 1

# print "Si dovrebbero inviare %d richieste" % indice_esterno
# geocodiamo = GeocodeEMDAT(nome_paese, 'Storm')
# geocodiamo.geolocate_accidents(locazioni_da_inviare_alla_geocodifica)
# geocodiamo.extract_country_shp()
# geocodiamo.calc_poligono_controllo()

# FASE SHAPEFILE CREATION
# shapiamo = CreateGeocodedShp(nome_paese,'Storm')
# shapiamo.creazione_file_shp()