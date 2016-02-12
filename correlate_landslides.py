__author__ = 'fabio.lana'

import pandas as pd
from sqlalchemy import create_engine, MetaData
import matplotlib.pyplot as plt
import requests
from pandas.io import wb
import pycountry
import numpy as np

from intermedi.utilita import all_plots

def richieste_wordlBank(iso3_paese):
    r_1980_1999 = requests.get('http://climatedataapi.worldbank.org/climateweb/rest/v1/country/mavg/pr/1980/1999/' + iso3_paese)

    lista_valori_mensili_pioggia = []
    dct_valori_mensili_pioggia = {}

    contatore = 1
    if r_1980_1999.status_code == 200:
        risposta = r_1980_1999.json()
        for valore_mensile in risposta[0]['monthVals']:
            lista_valori_mensili_pioggia.append(valore_mensile)
            dct_valori_mensili_pioggia[contatore] = valore_mensile
            contatore += 1
    else:
        print "Connection failed"

    return lista_valori_mensili_pioggia, dct_valori_mensili_pioggia

def emdat_events(ip_in, table_name):

    engine_in = create_engine(r'postgresql://geonode:geonode@' + ip_in + '/geonode-imports')
    
    try:
        conn_in = engine_in.connect()
        metadata_in = MetaData(conn_in, schema="em_dat")
    except Exception as e:
        print e.message

    df_in_sql = pd.read_sql_table(table_name, engine_in, schema=metadata_in.schema, index_col='index')

    return df_in_sql


def fao_prec_events(ip_in, table_name_rain):

    engine_in = create_engine(r'postgresql://geonode:geonode@' + ip_in + '/geonode-imports')

    try:
        conn_in = engine_in.connect()
        metadata_in = MetaData(conn_in, schema="public")
    except Exception as e:
        print e.message

    df_in_sql = pd.read_sql_table(table_name_rain, engine_in, schema=metadata_in.schema, index_col='adm2_code')
    df_in_sql.index = df_in_sql.index.str.rstrip()

    return df_in_sql

def main():


   ip_in = 'localhost'
   iso = 'NPL'
   oggetto_paese = pycountry.countries.get(alpha3=iso)
   paese_nome = oggetto_paese.name

   # indicators = ['NY.GDP.PCAP.KD', 'SP.POP.TOTL', 'SP.POP.0014.TO.ZS', 'SP.POP.65UP.TO.ZS', 'AG.LND.AGRI.ZS',
   #               'AG.YLD.CREL.KG', 'SP.RUR.TOTL', 'SH.STA.MALN.ZS', 'GC.BAL.CASH.GD.ZS', 'NE.EXP.GNFS.ZS',
   #               'NE.IMP.GNFS.ZS']
   #
   # iso2 = oggetto_paese.alpha2
   # dati_nazionali = wb.download(indicator=indicators, country=[iso2], start=2006, end=2014)
   # dati_nazionali.columns = ['GDP Per Capita','Total Pop', 'Pop Age 0-14', 'Pop Age 65-up',
   #              'Perc Agr Land','Cereal Yeld', 'Rural Population', 'Malnutrition Age<5',
   #              'Cash Surplus-Deficit','Export', 'Import', ]
   # print dati_nazionali
   # dati_nazionali['Total Pop'].plot(kind='bar')
   # plt.show()

   # print dati_nazionali['GDP Per Capita'].groupby(level=0).mean()

   # dati_nazionali['Importer'] = dati_nazionali['Export'] - dati_nazionali['Import']
   # print dati_nazionali

   # sub_indicators = ['SI.POV.NAHC','SI.POV.RUHC', 'SI.POV.URHC']
   # dati_sub_national = wb.download(indicator=indicators, country=[iso2], start=2006, end=2014)
   # print dati_sub_national
   # dati_sub_national.plot(kind='bar')
   # plt.show()

   table_name = 'Landslide_' + iso
   tabella = emdat_events(ip_in, table_name)
   tabella['mese_fine'] = tabella['end_date'].str.split('/').str.get(1)
   tabella['mese_inizio'] = tabella.start_date.str.split("/").str.get(1)
   conteggio = tabella['mese_fine'].value_counts()
   conteggio = conteggio.sort_index()
   print conteggio

   conteggio.plot(kind='bar')
   plt.title(paese_nome)
   plt.show()

   tabella_solo_landslides = tabella.loc[tabella['dis_subtype'] == 'Landslide']
   conteggio_solo_landslides = tabella_solo_landslides['mese_fine'].value_counts()
   conteggio_solo_landslides = conteggio_solo_landslides.sort_index()
   print conteggio_solo_landslides

   table_rain_name = 'sparc_month_prec'
   tabella_rain = fao_prec_events(ip_in, table_rain_name)
   # print tabella_rain.head()
   pioggia_adms2 = tabella_rain.loc[:, 'jan':]
   # print pioggia_adms2.head()
   # print pioggia_adms2.ix[3519]
   # print pioggia_adms2.info()
   # print pioggia_adms2.describe()
   vuzzulo = pioggia_adms2.loc['99953']

   # conteggio_dict = dict(conteggio)
   # for illo in conteggio_dict.iterkeys():
   #     print illo
   #
   # print conteggio_dict

   conteggio_solo_landslides.plot(kind='bar')
   plt.title(paese_nome)
   plt.show()
   # tabella.to_csv(table_name+ ".csv")

   valori_precipitazione_bancaMondiale_nazionale = richieste_wordlBank(iso)
   # print valori_precipitazione_bancaMondiale_nazionale[1]
   ivaloraggi = all_plots.plot_monthly_mean_wb(iso, valori_precipitazione_bancaMondiale_nazionale[0])
   ivaloraggi1 = all_plots.plot_monthly_mean_wb(iso, vuzzulo)

   # dict_finale = all_plots.historical_analysis_damages(paese_nome)
   # labella_y = "Precipitation (mm) Real Time World Bank"
   # all_plots.plot_monthly_danni("EM-DAT Registered Incidents", labella_y, iso, ivaloraggi, dict_finale)

if __name__ == "__main__":
    main()
