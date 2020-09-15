import time

import pandas as pd
import csv
import pathlib

fileNameCSV = "registroEstados.csv"
thisPath = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/') + '/'


def addNewLine(fecha,hora,nueva,SE1,SE2,EP,PNSM):
    #Fecha,Hora,Nueva?,SupuestoEstado,EstadoPing,PagNombSimMax,new_column
    PNSM = str(PNSM)
    PNSM = PNSM.replace("\\","/")
    PNSM = PNSM.split("/")[-1]
    with open(thisPath + fileNameCSV, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow([fecha,hora,nueva,SE1,SE2,EP,PNSM])

def isEmpty(file_name):
    print()

def createFile(file_name):
    if not proveExists():
        f = open(thisPath + file_name, 'w')
        f.close()

def proveExists(file_name):
    try:
        f = open(thisPath + file_name,'r')
        f.close()
        ema = True
    except Exception:
        ema = False
    return ema

def emptyCSVFile(file_name):
    if proveExists():
        with open(thisPath + file_name,'r') as f:
            firstLine = csv.reader(f).__next__()
        with open(thisPath + file_name,'w'):
            csv.writer(f).writerow(firstLine)

def duplicateFile(file_name):
    splitFileName = file_name.split('.')
    if len(splitFileName) == 2 and proveExists(file_name):
        cont = 0
        newName = splitFileName[0] + "_copia." + splitFileName[1]
        while proveExists(newName):
            cont = cont + 1
            newName = splitFileName[0] + "_copia" + str(cont) + "." + splitFileName[1]

        with open(thisPath + file_name,'r') as fToCopy:
            with open(newName,'w') as fToPaste:
                fToPaste.write(fToCopy.read())

def addColl(collName):
    df = pd.read_csv(thisPath + fileNameCSV)
    df.columns.data
    df[str(collName)] = "0"
    df.to_csv(fileNameCSV, index=False)

def reduceRegEstados(file_name):
    file_name = thisPath + file_name
    prev = []
    createFile(file_name)
    if isEmpty(file_name): # Si el archivo esta vacio creamos otro y le añadimos la estructura de CSV
        with open(file_name) as f:
            csv.writer(f).writerow(["Fecha","Hora","Nueva?","SupuestoEstadoMet1","SupuestoEstadoMet2","EstadoPing","PagNombSimMax"])

    with open(thisPath + fileNameCSV, 'r') as fCsv:
        csv_reader = csv.reader(fCsv)
        with open(thisPath + file_name, 'a') as fRegCSV:
            csv_apend = csv.writer(fRegCSV)
            cont = 0
            for l in csv_reader:
                if cont == 1:
                    csv_apend.writerow([1] + l)
                elif cont == len(csv_reader):
                    csv_apend.writerow([0] + l)
                elif cont > 1:
                    equal = True
                    for i in range(2, len(l)):
                         equal = equal and l[i] != prev[i]
                    if not equal:
                        csv_apend.writerow([0] + prev)
                        csv_apend.writerow([1]+l)
                prev = l
                cont = cont + 1
        duplicateFile(fileNameCSV)
        emptyCSVFile(fileNameCSV)
