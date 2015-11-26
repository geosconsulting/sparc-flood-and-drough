import os
import datetime

def raccolta_parametri(iso):

    anno_minimo = input("Starting Year: ")
    anno_massimo = input("Ending Year (max 2014): ")
    # numero_anni = input("Number of Years : ")
    numero_anni = anno_massimo - anno_minimo
    print("Fetching data for %d years" % numero_anni)
    mese = raw_input("Month : ")
    if len(mese) == 1:
        mese = "0" + mese
    giorno_inizio = input("Starting Day: ")
    # giorno_fine = giorno_inizio + 7
    giorno_fine = giorno_inizio + 8

    return anno_minimo, anno_massimo, numero_anni, mese,giorno_inizio, giorno_fine

def controlla_date(anno_inizio, mese_inizio, giorno_inizio):

    lista_mese_giorno = []
    data_iniziale = datetime.date(int(anno_inizio), int(mese_inizio), int(giorno_inizio))

    salto_giorni = datetime.timedelta(days=8)
    data_finale = data_iniziale + salto_giorni

    lista_giorni = [data_iniziale - salto_giorni for x in range(0, 8)]
    print lista_giorni

    import pandas as pd
    # datelist = pd.date_range(pd.datetime.today(), periods=100).tolist()
    datelist = pd.date_range(pd.datetime(int(anno_inizio), int(mese_inizio), int(giorno_inizio)), periods=8).tolist()
    print datelist

    giorno_data_inziale = data_iniziale.day
    giorno_data_finale = data_finale.day
    mese_data_inziale = data_iniziale.month
    mese_data_finale = data_finale.month

    lista_mese_giorno.append(str(mese_data_inziale) + "-" + str(giorno_data_inziale))
    lista_giorni.append(giorno_inizio)
    for indice in range(1, 8):
        range_date = datetime.timedelta(days=indice)
        giorni_successivi  = data_iniziale + range_date
        lista_mese_giorno.append(str(giorni_successivi.month) + "-" + str(giorni_successivi.day))
        lista_giorni.append(giorni_successivi)

    return lista_mese_giorno, giorno_data_inziale, mese_data_inziale , giorno_data_finale, mese_data_finale

def crea_file(anno_minimo, numero_anni, mese, giorno_inizio, giorno_fine):

    lista_anni = []
    lista_finale = []
    giorno_controllo = giorno_inizio
    for anno_inizio in range(0, numero_anni):
        lista_anni.append(anno_minimo + anno_inizio)

    for anno in lista_anni:
        while giorno_controllo < giorno_fine:
            lista_finale.append(str(anno) + "-" + str(mese) + "-" + str(giorno_controllo))
            giorno_controllo += 1
        giorno_controllo = giorno_inizio

    prima_parte = str(giorno_inizio) + str(giorno_fine-1)
    seconda_parte = str(anno_minimo) + str(max(lista_anni))
    file_path = 'dates/' + "req_" + str(prima_parte) + "_" + str(mese) + "_" + str(seconda_parte) + ".txt"
    if os.path.isfile(file_path):
        print "FILE DATES ESISTENTE"
        return file_path

    nuovo = open(file_path, mode='w')
    nuovo.write('"')
    lunghezza_lista = len(lista_finale)
    contatore = 1

    for illo in sorted(lista_finale):
        contatore += 1
        if contatore <= lunghezza_lista:
            nuovo.write(illo + "/")
        else:
            nuovo.write(illo)
    nuovo.write('"')
    nuovo.close()

    return file_path

def crea_file_avanzato(anno_minimo, numero_anni, lista_giorni):

    lista_anni = []
    lista_finale = []
    giorno_controllo = giorno_inizio
    for anno_inizio in range(0, numero_anni):
        lista_anni.append(anno_minimo + anno_inizio)

    # for anno in lista_anni:
    #     while giorno_controllo < giorno_fine:
    #         lista_finale.append(str(anno) + "-" + str(mese) + "-" + str(giorno_controllo))
    #         giorno_controllo += 1
    #     giorno_controllo = giorno_inizio
    #
    # prima_parte = str(giorno_inizio) + str(giorno_fine-1)
    # seconda_parte = str(anno_minimo) + str(max(lista_anni))
    # file_path = 'dates/' + "req_" + str(prima_parte) + "_" + str(mese) + "_" + str(seconda_parte) + ".txt"
    # if os.path.isfile(file_path):
    #     print "FILE DATES ESISTENTE"
    #     return file_path
    #
    # nuovo = open(file_path, mode='w')
    # nuovo.write('"')
    # lunghezza_lista = len(lista_finale)
    # contatore = 1
    #
    # for illo in sorted(lista_finale):
    #     contatore += 1
    #     if contatore <= lunghezza_lista:
    #         nuovo.write(illo + "/")
    #     else:
    #         nuovo.write(illo)
    # nuovo.write('"')
    # nuovo.close()
    #
    # return file_path

dati_raccolti = raccolta_parametri("pippo")
print dati_raccolti
liste_date = controlla_date(dati_raccolti[0], dati_raccolti[3], dati_raccolti[4])
print liste_date[0]
print liste_date[1:]
# crea_file(dati_raccolti[0],dati_raccolti[2],int(dati_raccolti[3]),dati_raccolti[4],dati_raccolti[5])

