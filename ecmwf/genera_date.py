import os
def crea_file(iso):

    anno_minimo = input("Starting Year: ")
    numero_anni = input("Number of Years : ")
    mese = raw_input("Month : ")
    if len(mese)==1:
        mese = "0" + mese
    giorno_inizio = input("Starting Day: ")
    # giorno_fine = giorno_inizio + 7
    giorno_fine = giorno_inizio + 8
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
