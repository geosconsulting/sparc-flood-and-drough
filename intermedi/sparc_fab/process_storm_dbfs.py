#!/usr/bin/python
from dbfpy import dbf
import os
import glob
import pycountry
import pandas as pd
from sqlalchemy import create_engine, MetaData


def prepare_storms_tables(paese):

    direttorio_radice = r"C:\sparc\projects\cyclones"
    direttorio = direttorio_radice + "\\" + paese_ricerca
    iso_paese = pycountry.countries.get(name=paese_ricerca).alpha3

    persone_rischio_cat_SaffirSimpson = {}
    for direttorio_principale, direttorio_secondario, file_vuoto in os.walk(direttorio):
        if direttorio_principale != direttorio:
            name_adm = direttorio_principale.split("\\")[5].split("_")[0]
            code_adm = direttorio_principale.split("\\")[5].split("_")[1]
            files_dbf = glob.glob(direttorio_principale + "/*.dbf")
            for file in files_dbf:
                fileName, fileExtension = os.path.splitext(file)
                if 'zs_' in fileName:
                    try:
                        if str(fileExtension) == '.dbf':
                            temporal_string = fileName.split("_")[3]
                            temporal_value = ''.join(x for x in temporal_string if x.isdigit())
                            in_dbf = dbf.Dbf(fileName + fileExtension)
                            for rec in in_dbf:
                                cat_ciclone = rec['VALUE']
                                num_people = rec['SUM']
                                indice_df = code_adm + "_" + str(rec['VALUE']) + "_" + temporal_string
                                # persone_rischio_cat_SaffirSimpson[indice_df] = {}
                                # persone_rischio_cat_SaffirSimpson[indice_df]['country'] = paese
                                # persone_rischio_cat_SaffirSimpson[indice_df]['iso_paese'] = iso_paese
                                # persone_rischio_cat_SaffirSimpson[indice_df]['code_adm'] = code_adm
                                # persone_rischio_cat_SaffirSimpson[indice_df]['iso_paese'] = iso_paese
                                # persone_rischio_cat_SaffirSimpson[indice_df]['cat_cycl'] = cat_ciclone
                                # persone_rischio_cat_SaffirSimpson[indice_df]['num_people'] = num_people
                                persone_rischio_cat_SaffirSimpson[indice_df] = {}
                                persone_rischio_cat_SaffirSimpson[indice_df]['iso_paese'] = iso_paese
                                persone_rischio_cat_SaffirSimpson[indice_df]['code_adm'] = code_adm
                                persone_rischio_cat_SaffirSimpson[indice_df]['cat_cycl'] = cat_ciclone
                                persone_rischio_cat_SaffirSimpson[indice_df]['num_people'] = num_people
                            in_dbf.close()
                    except:
                        pass
    return persone_rischio_cat_SaffirSimpson

paese_ricerca = "Cambodia"
dict_persone_at_risk = prepare_storms_tables(paese_ricerca)

df_people_at_risk = pd.DataFrame.from_dict(dict_persone_at_risk).transpose()
print df_people_at_risk

engine_out = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
try:
    conn_out = engine_out.connect()
except Exception as e:
    print e.message

table_name = "storm_" + str(paese_ricerca).lower() + "_ss"
df_people_at_risk.to_sql(table_name, engine_out, schema='pop_cat_ss')

