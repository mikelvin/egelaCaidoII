# Este codigo se encarga de guardar todas las versiones de eGela diferentes con el proposito de encontrar
# la version de egela caida.

import platform                 # Importar modulo platform y sp para obtener ping
import subprocess as sp

import requests                 # Importar el modulo requests para poder recibir la pagina
from bs4 import BeautifulSoup   # Importar BeatutifulSoup para analizar HTML
from html_similarity import style_similarity, structural_similarity, similarity

from registroDeEstados import regEstados
from WebPageArchive import archiveManager

import time

def main():
    prevFile = '.'
    prevFileName = ""
    url = 'https://egela.ehu.eus/?lang=eu'  # Esta es la URL de la pagina que se va a obtener
    trustUrl = 'google.com'

    archiveManager.updateCurrentArchive()
    duplicated = archiveManager.getDuplicateFiles()
    if duplicated:
        print("Hay achivos duplicados o muy parecidos, revisa estas direcciones:")
        for id, directions in enumerate(duplicated):
            print("\r", id, ": ", directions)
    else:
        print("No se han encontrado achivos duplicados o parecidos :,)")

    while True:
        ping_code = -1
        ping_meaning = ""
        newFile = False
        try:
            ping_code, ping_meaning = getPing("egela.ehu.eus",trustUrl)
            page = requests.get(url)        # Se obtiene la pagina como objeto Response y se guarda en la var. page

            errors = False
        except:
            errors = True

        if not errors :
            if structural_similarity(prevFile, page.text) != 1.0: # Se compara el contenido de la pagina actual con la pagina anterior

                maxSimArchiveName, maxSimil = encuentraArchivoMasParecido(page)

                # Si despues de compararla con todas las almacenadas la mayor similitud es menor entonces:
                if maxSimil <= 0.8:
                    nFileName = 'egel_' + str(int(time.time() // 1)) + '.html'
                    archiveManager.addArchive(nFileName, page.text) # El gestor se encargara de guardar esa pagina
                    maxSimArchiveName = nFileName
                    newFile = True

                prevFile = page.text
                prevFileName = maxSimArchiveName
            else:
                maxSimArchiveName = prevFileName
                maxSimil = 1.0

            regEstados.addNewLine(time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S"), newFile,
                                  proveIsFallen1(page), proveIsFallen2(maxSimArchiveName), ping_code,
                                  maxSimArchiveName)
        else:
           maxSimil = -1.0
           regEstados.addNewLine(time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S"), newFile, "ERR", "ERR", ping_code,
                                 "ERR")

           # en la carpeta de paginas
        print(time.ctime(),"/ Simil:", maxSimil,"/ PingCode:",ping_code,"; PingMeaning:",ping_meaning) # Se imprime la similitud para saber que el programa no se ha colgado
        time.sleep(10)

def encuentraArchivoMasParecido(pageRequest):
    # Con el siguiente codigo se compara la pagina solicitada con todas las paginas que disponemos en
    #   WebPageArchive en busca del archivo mas parecido
    maxSimil = -1.0
    maxSimArchiveName = ""

    for fileData in archiveManager.getAllFilesDetailed():  # Se le pide al gestor de archivos todos los datos/contenidos de las paginas guardadas
        comp = structural_similarity(fileData[1], pageRequest.text)  # Se comapara cada uno de los datos con la pagina solicitada
        if maxSimil < comp:
            maxSimArchiveName = fileData[0]  # Se almacena cual es el nombre del archivo con similitud mayor para no guardar
            maxSimil = comp  # la misma pagina en el regstro y se guarda tambien dicha similitud
        if maxSimil == 1.0:
            break  # Si encuentra una similitud de 1 quiere decir que la pagina ya esta en el registro
    return maxSimArchiveName, maxSimil


def getPing(target ,trust):

    statusT, resultT = sp.getstatusoutput(
        "ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + str(trust))

    statusH, resultH = sp.getstatusoutput(
        "ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + str(target))

    if statusT == 0:
        if statusH == 0:
            # print("System " + str(target) + " is UP !")
            meaning = "ON"
            ema = 1
        else:
            # print("System " + str(target) + " is DOWN !")
            meaning = "OFF"
            ema = 0
    else:
        if statusH == 0:
            meaning = "T-OFF/V-ON"
            ema = 2
        else:
            meaning = "T-OFF/V-OFF"
            ema = 3
        # print("System can't connect to reference host: " + str(trust))

    return ema, meaning

def proveIsFallen1(pageRequest):
    '''
    Este metodo comprueba si la pagina que se ha solicitado es la pagina en la que se puede acceder a la plataforma o
    es la pagina que informa que esta se ha caido. Lo confirma comprobando si la pagina solicitada contiene cierto
    codigo HTML. Para ello usa el modulo BeatutifulSoup

    Input: Request object
    Output: Boolean
    '''
    soup = BeautifulSoup(pageRequest.text, 'html.parser')  # Crear objeto BeautifullSoup de la pagina recibida

    egela_logBox = soup.find(class_='signupmessage')    # Busca y obtiene la caja de inicio de sesion
    egela_logForm = soup.find('form', class_='m-t-1')   # Busca y obtiene el formulario de inicio de sesion

    val_Total = bool(egela_logForm) and bool(egela_logBox)   #Comprueba si existe tanto la caja como el formulario de inicio de sesion
    if bool(egela_logForm):
        # Comprueba si el link del formlario es el adecuado
        val_Total = val_Total and (egela_logForm.get('action') == 'https://egela.ehu.eus/login/index.php')

    return val_Total

def proveIsFallen2(pageName):
    '''
    Este metodo comprueba si la pagina que se ha solicitado es la pagina en la que se puede acceder a la plataforma o
    es la pagina que informa que esta se ha caido. Lo confirma usando un registro de paginas webs. Compara la pagina solicitada
    con todas las paginas del registro hasta conseguir una coincidencia. Una vez comparadas y despues de haber
    obtenido alguna coincidencia, es necesario otro registro (Registro analitico) en el que por cada pagina web obtenida en
    el registro de paginas, se especifica si estas corresponden a la respuesta del servidor operativo o caido.
    Mirando la categoria en la que se encuentra la pagina mas similar en el registro de paginas webs a la pagina a analizar,
    (usando el registro analitico) se determina el estado de la pagina a analizar.
    '''
    return archiveManager.getArchiveData(pageName)
main()