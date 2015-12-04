#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fabio.lana'

from Tkinter import *
import tkMessageBox
import ttk
import psycopg2

class AppECMWF:

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

        self.lista_paesi = all_country_db()

        finestra.geometry("450x250+30+30")

        self.area_messaggi = Text(finestra, background="black", foreground="green")
        self.area_messaggi.place(x=18, y=30, width=282, height=215)

        self.scr = Scrollbar(finestra, command=self.area_messaggi.yview)
        self.scr.place(x=8, y= 30, width=10, height=215)
        self.area_messaggi.config(yscrollcommand=self.scr.set)

        self.box_value_adm0 = StringVar()
        self.box_adm0 = ttk.Combobox(finestra, textvariable=self.box_value_adm0)
        self.box_adm0['values'] = self.lista_paesi
        self.box_adm0.current(0)
        self.box_adm0.place(x=10, y=2, width=250, height=25)

        self.listbox = Listbox(finestra)
        self.listbox.place(x=310, y=70, width=130, height=150)

        self.button_add_countries = Button(finestra, text="Add Country", fg="blue", command=self.aggiungi)
        # self.button_add_countries.bind('<Button-1>', lambda scelta: scegli_azione("add"))
        self.button_add_countries.place(x=275, y=3, width=100, height=25)

        self.bbox_list = []
        self.button_calc_anomalies = Button(finestra, text="Start Analysis", fg="red", command = self.calcola)
        # self.button_calc_anomalies.bind('<Button-1>', lambda scelta: scegli_azione("calc"))
        self.button_calc_anomalies.place(x=310, y=35, width=130, height=25)

        finestra.mainloop()


    def aggiungi(self):

        paese = self.box_value_adm0.get()
        self.listbox.insert(END, paese)

        self.cur = self.conn.cursor()
        comando = "SELECT ST_Extent(geom) as bbox FROM sparc_gaul_wfp_iso WHERE adm0_name = '" + paese + "';"

        try:
            self.cur.execute(comando)
        except psycopg2.ProgrammingError as laTabellaNonEsiste:
            descrizione_errore = laTabellaNonEsiste.pgerror
            codice_errore = laTabellaNonEsiste.pgcode
            print descrizione_errore, codice_errore
            return codice_errore
        for paese in self.cur:
            self.bbox_list.append(paese[0])


    def calcola(self):

        print self.bbox_list
        # verifica = tkMessageBox.askyesno("Warning", "The calculation can take a very long time!!\nContinue?")


root = Tk()
root.title("ECMWF Data Analysis")
app = AppECMWF(root)




