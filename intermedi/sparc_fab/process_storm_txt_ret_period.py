#!/usr/bin/python
import os
import glob
import pandas as pd
from sqlalchemy import create_engine


def fetch_txt_ret_period():

    direttorio_radice = r"C:\sparc\projects\cyclones"

    lista_txt = []
    for root, dirs, files in os.walk(direttorio_radice):
        componenti,num_componenti = root.split("\\"), len(root.split("\\"))
        if num_componenti == 5:
            file_txt = glob.glob(root + "/*.txt")
            # print file_txt
            lista_txt.append(file_txt)

    return lista_txt

engine_out = create_engine(r'postgresql://geonode:geonode@localhost/geonode-imports')
try:
    conn_out = engine_out.connect()
except Exception as e:
    print e.message

lista_file_testo = fetch_txt_ret_period()
for file_di_testo in lista_file_testo:
    paese = file_di_testo[0].split("\\")[4]
    df_tempi_ritorno = pd.DataFrame.from_csv(file_di_testo[0])
    table_name = "storm_" + str(paese).lower() + "_rp_adm2"
    df_tempi_ritorno.to_sql(table_name, engine_out, schema='ret_per_adm2')

