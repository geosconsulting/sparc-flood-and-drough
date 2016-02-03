#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import tkMessageBox
import ttk
import psycopg2
import datetime
import os
from calendar import monthrange

import NASA_FTP_Connections
import  TRMM_GPM_Processor

class AppNASA:

    def __init__(self, finestra):

        self.dbname = "geonode-imports"
        self.user = "geonode"
        self.password = "geonode"

        try:
            connection_string = "dbname=%s user=%s password=%s" % (self.dbname, self.user, self.password)
            self.conn = psycopg2.connect(connection_string)
        except Exception as e:
            print e.message

        self.cur = self.conn.cursor()

        def all_country_db():

            self.cur = self.conn.cursor()
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

        finestra.geometry("860x390+30+30")

        self.lista_paesi = all_country_db()
        self.parte_3lettere_per_file = []

        self.now = datetime.datetime.now()
        self.mese_inizio = self.now.month
        self.giorno_inizio = self.now.day

        self.area_messaggi = Text(finestra, background="black", foreground="green", font=("Helvetica",8))
        self.area_messaggi.place(x=18, y=30, width=425, height=350)

        self.scr = Scrollbar(finestra, command=self.area_messaggi.yview)
        self.scr.place(x=8, y=30, width=10, height=350)
        self.area_messaggi.config(yscrollcommand=self.scr.set)

        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(finestra, textvariable=self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.place(x=10, y=2, width=250, height=25)

        self.button_add_countries = Button(finestra, text="Add Country", fg="blue", command=self.aggiungi_paese_alla_lista_di_processo)
        self.button_add_countries.place(x=260, y=3, width=80, height=25)

        self.listbox_countries = Listbox(finestra)
        self.listbox_countries.place(x=600, y=30, width=250, height=125)

        self.listbox_nasa = Listbox(finestra)
        self.listbox_nasa.place(x=450, y=170, width=400, height=175)

        self.button_TRMM_data = Button(finestra, text="TRMM Data", fg="red", command=self.TRMM_processing)
        self.button_TRMM_data.place(x=340, y=3, width=80, height=25)

        self.button_TRMM_data = Button(finestra, text="GPM Data", fg="red", command=self.GPM_processing)
        self.button_TRMM_data.place(x=420, y=3, width=80, height=25)

        self.button_IMERG_data = Button(finestra, text="IMERG Data", fg="red", command = self.IMERG_processing)
        self.button_IMERG_data.place(x=500, y=3, width=80, height=25)

        self.area_oggi = Entry(finestra, background="white", foreground="red",)
        self.area_oggi.place(x=775, y=3, width=75, height=25)
        self.area_oggi.insert(INSERT, str(self.now.date()))

        self.box_giorni_val = StringVar()
        self.box_giorni = ttk.Combobox(finestra, textvariable=self.box_giorni_val, width=7)
        self.box_giorni['values'] = range(1, 31)
        self.box_giorni.current(0)
        self.box_giorni.place(x=450, y=90, width=130)

        mesi = list(range(1, 12))
        self.box_mese_val = StringVar()
        self.box_mese = ttk.Combobox(finestra, textvariable=self.box_mese_val, width=7)
        self.box_mese['values'] = mesi
        self.box_mese.current(0)
        self.box_mese.place(x=450, y=115, width=130)


        #Scelta anni minimo massimo per analisi corrente
        lista_anni = list(range(1998, self.now.year + 1))
        self.box_year_val = StringVar()
        self.box_year = ttk.Combobox(finestra, textvariable=self.box_year_val, width=7)
        self.box_year['values'] = lista_anni
        self.box_year.current(0)
        self.box_year.place(x=450, y=140, width=130)

        # def cambia_lista_giorni(anno,mese):
        #
        #     print anno, mese
        #     # anno = self.box_year_val
        #     # mese = self.box_mese_val
        #
        #     diff = monthrange(int(anno),int(mese))
        #     print diff
        #     ini, fin = diff[0], diff[1]
        #     self.box_giorni['values'] = range(ini, fin)

        # self.box_mese.bind('<<ComboboxSelected>>', cambia_lista_giorni(self.box_year_val.get(), self.box_mese_val.get()))
        # self.box_year.bind('<<ComboboxSelected>>', cambia_lista_giorni(self.box_year_val.get(), self.box_mese_val.get()))

        self.button_anomalies = Button(finestra, text="Precipitation Anomalies", fg="red", command=self.calcola_bbox_parteISO)
        self.button_anomalies.place(x=450, y=350, width=150, height=25)

        self.button_spi = Button(finestra, text="SPI Calculator", fg="red", command=self.calcola_bbox_parteISO)
        self.button_spi.place(x=650, y=350, width=150, height=25)

        finestra.mainloop()

    def aggiungi_paese_alla_lista_di_processo(self):

        paese = self.box_value_adm0.get()
        self.listbox_countries.insert(END, paese)

    def calcola_bbox_parteISO(self):

        lista_comandi = []
        self.cur_bbox = self.conn.cursor()

        num_items = self.listbox_countries.size()
        for illo in range(0, num_items):
            pattivo = self.listbox_countries.get(illo, last=None)
            lista_comandi.append("SELECT ST_Extent(geom) as bbox FROM sparc_gaul_wfp_iso WHERE adm0_name = '" + str(pattivo) + "';")

        self.dict_coords = {}
        for comando in lista_comandi:
            # self.area_messaggi.insert(INSERT, comando + '\n')
            try:
                self.cur_bbox.execute(comando)
                for la_stringa_coords in self.cur_bbox:
                    coordinate = (la_stringa_coords[0].split("(")[1].split(")")[0])
                    coordinateX, coordinateY = coordinate.split(",")
                    min_x, min_y = coordinateX.split()
                    max_x, max_y = coordinateY.split()
                    self.dict_coords = {'xmin': min_x, 'ymin': min_y, 'xmax': max_x, 'ymax': max_y}
                    messaggio = 'xmin %s - min_x %s - min_y %s - max_x %s' % (min_x, min_y, max_x, max_y)
                    self.area_messaggi.insert(INSERT, messaggio + '\n')
            except psycopg2.ProgrammingError as laTabellaNonEsiste:
                descrizione_errore = laTabellaNonEsiste.pgerror
                codice_errore = laTabellaNonEsiste.pgcode
                print descrizione_errore, codice_errore
                return codice_errore
        return self.dict_coords

    def TRMM_processing(self):


        messaggio, files_disponibili = NASA_FTP_Connections.FtpConnectionFilesGatheringTRMM(self.box_year_val.get(), self.box_mese_val.get(), self.box_giorni_val.get())
        # tkMessageBox.showinfo("Connection", messaggio)

        self.listbox_nasa.delete(0, END)

        if len(files_disponibili) > 0:
            self.area_messaggi.insert(INSERT, messaggio)
            lista_ftp = []

            for file_disponibile in files_disponibili:
                lista_ftp.append(file_disponibile)
                self.listbox_nasa.insert(END, file_disponibile)

    def IMERG_processing(self):

        code, messaggio, files_disponibili = NASA_FTP_Connections.FtpConnectionFilesGatheringIMERG(self.box_year_val.get(), self.box_mese_val.get())

        if code == 0:
            tkMessageBox.showinfo("Warning", messaggio)
            pass
        else:
            self.listbox_nasa.delete(0, END)
            if len(files_disponibili) > 0:
                self.area_messaggi.insert(INSERT, messaggio)
                lista_ftp = []

                for file_disponibile in files_disponibili:
                    lista_ftp.append(file_disponibile)
                    self.listbox_nasa.insert(END, file_disponibile)
            else:
                tkMessageBox.showinfo("Warning", messaggio)
                pass

    def GPM_processing(self):

        tkMessageBox.showinfo("Warning", "Almost Complete")

        # code, messaggio, files_disponibili = NASA_FTP_Connections.FtpConnectionFilesGatheringGPM(self.box_year_val.get(), self.box_mese_val.get())

        # if code == 0:
        #     tkMessageBox.showinfo("Warning", messaggio)
        #     pass
        # else:
        #     self.listbox_nasa.delete(0, END)
        #     if len(files_disponibili) > 0:
        #         self.area_messaggi.insert(INSERT, messaggio)
        #         lista_ftp = []
        #
        #         for file_disponibile in files_disponibili:
        #             lista_ftp.append(file_disponibile)
        #             self.listbox_nasa.insert(END, file_disponibile)
        #     else:
        #         tkMessageBox.showinfo("Warning", messaggio)
        #         pass

root = Tk()
root.title("Precipitation Data Analysis")
app = AppNASA(root)




