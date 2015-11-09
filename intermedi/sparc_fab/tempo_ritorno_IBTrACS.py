# -*- coding: utf-8 -*
import os
from osgeo import ogr
ogr.UseExceptions()
import pycountry
from math import floor

# COSTANTI
PROJ_DIR = "c:/sparc/projects/cyclones/"
DRIVER = ogr.GetDriverByName("ESRI Shapefile")
CYLONES_RECLASSED_DIR = "C:/sparc/input_data/cyclones_data/"
CYCLONES_TRACKS_DIR = "C:/sparc/input_data/cyclones_data/"
SHAPE_COUNTRIES = "c:/sparc/input_data/gaul/gaul_wfp_iso.shp"
SHAPE_TRACKS = CYCLONES_TRACKS_DIR + "cy_tracks.shp"

FIELD_NAME_COUNTRY = "ADM0_NAME"
FIELD_ISO_COUNTRY = "ADM0_CODE"
FIELD_NAME_ADMIN1 = "ADM1_NAME"
FIELD_ISO_ADMIN1 = "ADM1_CODE"
FIELD_NAME_ADMIN2 = "ADM2_NAME"
FIELD_ISO_ADMIN2 = "ADM2_CODE"

filter_field_adm2 = "ADM0_NAME,ADM0_CODE,ADM1_NAME,ADM1_CODE,ADM2_NAME,ADM2_CODE"
filter_field_cyclones = "gid,ev_id,iso3_year,year,start_date,wind,pressure,other_name,serial_num"

def file_structure_creation(paese, admin_name, adm_code,contatore):

        os.chdir(PROJ_DIR)
        country_low = str(paese).lower()
        admin_low = admin_name.lower() + "_" + str(adm_code)
        if os.path.exists(country_low):
            os.chdir(PROJ_DIR + country_low)
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))
        else:
            os.chdir(PROJ_DIR)
            os.mkdir(country_low)
            os.chdir(PROJ_DIR + country_low)
            admin_low = admin_name.lower() + "_" + str(adm_code)
            #print admin_low
            if os.path.exists(admin_low):
                pass
            else:
                os.mkdir(admin_low.replace("\n", ""))

        file_calcoli = PROJ_DIR + paese + "/" + paese + ".txt"
        if contatore == 1:
            if os.path.exists(file_calcoli):
                os.remove(file_calcoli)
            probability_list = open(PROJ_DIR + paese + "/" + paese + ".txt", "a")
            probability_list.write("id,num_tracks,min_year,max_year,rp,prob\n")
        else:
            probability_list = open(PROJ_DIR + paese + "/" + paese + ".txt", "a")

        return admin_low, probability_list

def extract_admin(shape_countries_pass, paese, adm_dir, code_adm):

    shapefile_countries = DRIVER.Open(shape_countries_pass)
    layer_admins = shapefile_countries.GetLayer()

    # Get the input Layer
    inDataSource = DRIVER.Open(SHAPE_COUNTRIES, 0)
    inLayer = inDataSource.GetLayer()
    inLayerProj = inLayer.GetSpatialRef()
    inLayer.SetAttributeFilter("ADM2_CODE=" + code_adm)
    conteggio_admin = layer_admins.GetFeatureCount()

    # Create the output LayerS
    outShapefile = os.path.join(PROJ_DIR + paese + "/" + str(adm_dir).lower() + "/" + code_adm + ".shp")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        DRIVER.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = DRIVER.CreateDataSource(outShapefile)
    out_lyr_name = str(code_adm)
    out_layer = outDataSource.CreateLayer(out_lyr_name, inLayerProj, geom_type=ogr.wkbMultiPolygon)

    # Add input Layer Fields to the output Layer if it is the one we want
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        if fieldName not in filter_field_adm2:
            continue
        out_layer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = out_layer.GetLayerDefn()

    # Add features to the ouput Layer
    for inFeature in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            fieldDefn = outLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            if fieldName not in filter_field_adm2:
                continue
            dascrivere = inFeature.GetField(fieldName)
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), dascrivere)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom.Clone())

        # Add new feature to output Layer
        out_layer.CreateFeature(outFeature)

        # print "Admin %s extracted" % code_adm

    # Close DataSources
    inDataSource.Destroy()
    outDataSource.Destroy()

    return conteggio_admin

def extract_cyclones(shape_tracks_name, paese, adm_dir, code_adm):

    # path_admin_exctracted = PROJ_DIR + adm + ".shp"
    path_admin_exctracted = PROJ_DIR + paese + "/" + str(adm_dir).lower() + "/" + code_adm + ".shp"
    shapefile_adm = DRIVER.Open(path_admin_exctracted)
    layer_admins = shapefile_adm.GetLayer()

    poly_adm2 = layer_admins.GetNextFeature()
    poly = poly_adm2.GetGeometryRef()

    # Get the input Layer
    inDriver = DRIVER
    inDataSource = inDriver.Open(shape_tracks_name, 0)
    inLayer = inDataSource.GetLayer()
    inLayer.SetSpatialFilter(poly)
    num_tracce_instersect = inLayer.GetFeatureCount()
    inLayerProj = inLayer.GetSpatialRef()

    # outShapefile = os.path.join(PROJ_DIR + str(code) + "_cy.shp")
    outShapefile = os.path.join(PROJ_DIR + paese + "/" + str(adm_dir).lower() + "/" + code_adm + "_cy.shp")
    outDriver = DRIVER
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    out_lyr_name = str(code_adm) + "_cy"
    out_layer = outDataSource.CreateLayer(out_lyr_name, inLayerProj, geom_type=ogr.wkbMultiLineString)

    # Add input Layer Fields to the output Layer if it is the one we want
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        if fieldName not in filter_field_cyclones:
             continue
        out_layer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = out_layer.GetLayerDefn()

    # Add features to the ouput Layer
    for inFeature in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            fieldDefn = outLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            if fieldName not in filter_field_cyclones:
                continue
            dascrivere = inFeature.GetField(fieldName)
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), dascrivere)

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom.Clone())

        # Add new feature to output Layer
        out_layer.CreateFeature(outFeature)

        # Close DataSources
    inDataSource.Destroy()
    outDataSource.Destroy()

    return outShapefile, num_tracce_instersect

def tempo_ritorno(tracce_estratte):

    inDriver = DRIVER
    inDataSource = inDriver.Open(tracce_estratte, 0)
    layer_tracks = inDataSource.GetLayer()
    nomi = set()
    anni = set()
    feature = layer_tracks.GetNextFeature()
    while feature:
        nomi.add(feature.other_name)
        anni.add(feature.year)
        feature = layer_tracks.GetNextFeature()

    num_evts = 1
    sum_rps = 0
    dict_anni = {}

    for anno in anni:
        dict_anni[num_evts] = anno
        num_evts += 1

    for chiave, anno in dict_anni.iteritems():
        # print dict_anni[chiave]
        if chiave > 1:
            indice1 = chiave - 1
            indice2 = chiave
            differenza = abs(dict_anni[indice1] - dict_anni[indice2])
            sum_rps = sum_rps + differenza


    return dict_anni, float(sum_rps), float(num_evts-2)

def floored_percentage(val, digits):
    val *= 10 ** (digits + 2)
    return '{1:.{0}f}%'.format(digits, floor(val) / 10 ** digits)

def pulisci_admin2(nome_zozzo):

    import re,unicodedata

    no_dash = re.sub('-', '_', nome_zozzo)
    no_space = re.sub(' ', '', no_dash)
    no_slash = re.sub('/', '_', no_space)
    no_apice = re.sub('\'', '', no_slash)
    no_bad_char = re.sub(r'-/\([^)]*\)', '', no_apice)
    unicode_pulito = no_bad_char.decode('utf-8')
    nome_pulito = unicodedata.normalize('NFKD', unicode_pulito).encode('ascii', 'ignore')

    return nome_pulito

def iterare_sul_paese(iso3):

    paese = pycountry.countries.get(alpha3 = iso3)
    iso = paese.alpha3
    nome_paese = paese.name

    dataSource = DRIVER.Open(SHAPE_COUNTRIES, 0)
    inLayer = dataSource.GetLayer()
    inLayerProj = inLayer.GetSpatialRef()
    string_filtro = "iso3='" + str(iso) + "'"
    inLayer.SetAttributeFilter(string_filtro)
    conteggio_admin = inLayer.GetFeatureCount()
    print "There are %d administrative areas in %s "  % (conteggio_admin,nome_paese)
    contatore = 1
    for feature in inLayer:
        nome = feature.GetField("ADM2_NAME")
        codice = feature.GetField("ADM2_CODE")
        nome_da_usare = pulisci_admin2(nome)

        dir_adm, probability_list = file_structure_creation(nome_paese, nome_da_usare, codice, contatore)
        parti_admin_dir = dir_adm.split("_")
        num_ = len(parti_admin_dir)
        # print num_
        code_adm = parti_admin_dir[num_-1]

        extract_admin(SHAPE_COUNTRIES, nome_paese, dir_adm,code_adm)
        tracce_estratte, num_tracce = extract_cyclones(SHAPE_TRACKS, nome_paese, dir_adm, code_adm)
        # nome_shp = tracce_estratte.split("/")[4].split(".shp")[0]
        # print nome_shp
        # nome_senza_shp = tracce_estratte.split(".shp")[0]
        # print nome_senza_shp
        # path_shp = tracce_estratte.split(nome_shp)[0]
        # print path_shp
        lista_anni, somma_anni, numero_eventi = tempo_ritorno(tracce_estratte)
        print lista_anni
        if numero_eventi > 0:
            rp = float(somma_anni/numero_eventi)
            prob = 1.00/rp
            min_anno = min(lista_anni.values())
            max_anno = max(lista_anni.values())
            print "Return period %.2f with annual probability of %s" % (rp, floored_percentage(1.00/rp, 0))
        else:
            rp = 99999
            prob = 99999
            min_anno = 99999
            max_anno = 99999

        stringa_di_scrittura = code_adm + "," + str(num_tracce) + "," + str(min_anno) + "," + str(max_anno) + "," + str(rp) + "," + str(prob) + "\n"
        probability_list.write(stringa_di_scrittura)

        contatore += 1

    probability_list.close()

    # os.chdir(CYLONES_RECLASSED_DIR)
    # category_reclass_yearly_tifs = glob.glob("*.tif")

iterare_sul_paese('MWI')