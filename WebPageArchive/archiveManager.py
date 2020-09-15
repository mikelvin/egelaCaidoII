import pathlib
from os import remove
import csv
from html_similarity import structural_similarity

thisPath = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/') + '/'
egelaCaidoName = ''
# print(__file__)
def addArchive(name, archiveText):
    uniqueName = True
    filesPath = open(thisPath + 'currentArchivesPath.txt', 'r')
    for files in filesPath:
        uniqueName = uniqueName and files != thisPath + name + '\n'
    filesPath.close()
    if uniqueName:
        filesPath = open(thisPath + 'currentArchivesPath.txt', 'a+')
        newFile = open(thisPath + name, 'w', encoding="utf-8")
        newFile.write(archiveText)
        filesPath.write(thisPath + name + '\n')
        newFile.close()
        filesPath.close()
        print('Archivo añadido:', name)
    else:
        print('No se ha añadido por que ya hay una archivo con el mismo nombre bebe')


def getAllFiles():
    arrDetailed = getAllFilesDetailed()
    arr = ['*']*arrDetailed.__len__()
    kont = 0
    for file in arrDetailed:
        arr[kont] =  file[1]
        kont = kont + 1
    return arr

def getAllFilesDetailed():
    filesPath = open(thisPath + 'currentArchivesPath.txt', 'r')
    lines = 0
    for i in filesPath:
        lines = lines + 1

    arr = [[0] * 2 for i in range(lines)]
    filesPath.close()

    filesPath = open(thisPath + 'currentArchivesPath.txt', 'r')
    kont = 0
    for file in filesPath:
        filesName = file.replace('\n', '')
        if filesName:
            currFile = open(filesName, 'r')
            arr[kont][1] = currFile.read()
            arr[kont][0] = filesName
            currFile.close()

        kont = kont + 1

    filesPath.close()
    return arr

def updateCurrentArchive(notif = True):
    i = sorted(pathlib.Path(thisPath).glob('*.html'))
    filesPath = open(thisPath + 'currentArchivesPath.txt', 'w')
    for htmFiles in i:
        filesPath.write(str(htmFiles.absolute())+'\n')
    if notif:
        print('currentArchivesPath.txt', 'UPDATED')

def getDuplicateFiles():
    allFilesDetailed = getAllFilesDetailed()
    arrOfDuplicate = []
    for i in range(0, len(allFilesDetailed)):
        for j in range(i+1,len(allFilesDetailed)):
            if structural_similarity(allFilesDetailed[i][1],allFilesDetailed[j][1]) == 1.0:
                arrOfDuplicate.append(allFilesDetailed[i][0])
                break

    return arrOfDuplicate

def removeHtmlFile(htmlFileName):
    updateCurrentArchive(False)
    htmlFileName = str(htmlFileName)
    contains = False
    if htmlFileName.rsplit('.').pop().upper() == "HTML":
        filesPath = open(thisPath + 'currentArchivesPath.txt', 'r')
        for files in filesPath:
            contains = contains or files == htmlFileName + '\n'
            if contains:
                break
        filesPath.close()
        if contains:
            remove(htmlFileName)
            print('Archivo "', htmlFileName, '" eliminado satisfactoriamente.',
                  '\nSe va a actualizar el registro de archivos:')
            updateCurrentArchive()

    if not contains:
        print('No se ha podido eliminar el archivo "', htmlFileName, '": No es HTML o no existe en el archivo')

def getEgelaCaido():
    file = open(egelaCaidoName,'r')
    ret = file.read()
    file.close()
    return ret


def iniciarClasificadorDePaginas(showInfo=False):
    existingFileNames = []
    for htmlFilePath in sorted(pathlib.Path(thisPath).glob('*.html')):
        existingFileNames.append(str(htmlFilePath.absolute()).split('\\').pop())

    countTOT = len(existingFileNames)
    countCLAS = 0
    useless = []
    rowNumb = 1
    with open("archivesData.csv", 'r') as f:
        csvFile = csv.reader(f)
        for row in csvFile:
            usefullRow = False
            if len(row) >= 2:
                for existingFileName in existingFileNames:
                    if existingFileName == row[0]:
                        usefullRow = True
                        if not row[1].__contains__('?'):
                            countCLAS = countCLAS + 1
                        existingFileNames.remove(existingFileName)
                        break
                if not usefullRow:
                    useless.append([rowNumb, row[0]])
            rowNumb = rowNumb + 1

    for fNoReg in existingFileNames:
        with open("archivesData.csv", 'a') as f:
            f.write(fNoReg + ",?\n")

    if showInfo:
        if countTOT != countCLAS:
            resum = "Falta(n) " + str(countTOT - countCLAS) + " pagina(s) por clasificar."
        else:
            resum = "Todas las paginas estan clasificadas :)"
        print("-------------------------------------\n"
              "Clasificador de paginas INICIALIZADO:\n"
              "De la(s)", countTOT, "pagina(s) capturada(s)", countCLAS, "esta(n) clasificada(s), es decir:", resum)
        if len(useless) != 0:
            print("Ademas hay archivos registrados en archivesData.csv que no existen:")
            for uselessArchives in useless:
                print("\t- Linea:",uselessArchives[0],"| Nombre:", uselessArchives[1])

def getArchiveData(pageName):
    pageName = str(pageName).replace("/","\\").split("\\")[-1]
    with open("archivesData.csv","r") as f:
        csvReader = csv.reader(f)
        pageState = "?"
        for row in csvReader:
            if len(row) >= 2:
                if row[0] == pageName:
                    pageState = row[1]
                    if pageState != "ON" or pageState != "OFF":
                        pageState = "?"
                    break
    return pageState