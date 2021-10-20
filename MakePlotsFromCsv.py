import pandas as pd
import matplotlib.pyplot as plt
import statistics as matStat
from dateutil import parser
from datetime import datetime, date
import glob
import matplotlib.pyplot as plt
import statistics as matStat
from dateutil import parser
from datetime import datetime, date
import re
import warnings
import numpy as np
warnings.warn("deprecated", DeprecationWarning)

import Experiment

meditationFilesNamesList = glob.glob('*_meditation.csv')
attentionFilesNamesList = glob.glob('*_attention.csv')

def GetTestSubjectNameFromFile(fileName):
    endOfNamePosition = fileName.find("_meditation.csv")
    if endOfNamePosition != -1:
        return fileName[:endOfNamePosition]
    
    endOfNamePosition = fileName.find("_attention.csv")    
    if endOfNamePosition != -1:
        return fileName[:endOfNamePosition]

    return 0

# Функция проверки того, что у meditation-файла есть сопряженный файл
def IsMeditationFileHaveMateFile(meditationFilesName):
    subjectName = GetTestSubjectNameFromFile(meditationFilesName)
    ret = False
    if subjectName != 0:
        for attentionFileName in attentionFilesNamesList:
            if attentionFileName.find(subjectName) != -1:
                ret = True
                break

    return ret

def SavePlot(testSubjectName):
    plot_graph(testSubjectName,10)
    print("Сохранен график для", testSubjectName)
    return 0

# Функция запуска процедуры построения графика для файлов
def main():
    if len(meditationFilesNamesList) > 0:
        for meditationFileName in meditationFilesNamesList:
            if IsMeditationFileHaveMateFile(meditationFileName):
                testSubjectName = GetTestSubjectNameFromFile(meditationFileName)
                experimnent = Experiment.Experiment(testSubjectName)     


def plot_graph(testSubjectName,knn):
    testSubjectName = testSubjectName
    testSubjectMeditation = pd.read_csv(testSubjectName+r"_meditation.csv", sep=';')
    testSubjectAttention = pd.read_csv(testSubjectName+r'_attention.csv', sep=';')

    lesserSize = min(len(testSubjectMeditation),len(testSubjectAttention))

    testSubjectMeditation = testSubjectMeditation[0:lesserSize]
    testSubjectAttention = testSubjectAttention[0:lesserSize]

    pristineMeditation = testSubjectMeditation['ESenseMeditation']
    pristineAttention = testSubjectAttention['ESenseAttention']

    pristinePacketContext = testSubjectMeditation['PacketContext']

    countOfRowsMeditation = len(pristineMeditation)
    countOfRowsAttention = len(pristineAttention)

    testSubjectMeditation['ParseTime'][0]

    for i in range(0,countOfRowsMeditation):
        result = re.match(r'^.+? (\d+?:\d+?:\d+?):.+?', testSubjectMeditation['ParseTime'][i])
        onlyTimeString = result.group(1)
        testSubjectMeditation['ParseTime'][i] = onlyTimeString
    
    for i in range(0,countOfRowsAttention):
        result = re.match(r'^.+? (\d+?:\d+?:\d+?):.+?', testSubjectAttention['ParseTime'][i])
        onlyTimeString = result.group(1)
        testSubjectAttention['ParseTime'][i] = onlyTimeString

    approxMeditation = knn_regression_approx(pristineMeditation,knn)
    approxAttention = knn_regression_approx(pristineAttention,knn)

    meditationMean = np.mean(approxMeditation)
    attentionMean = np.mean(approxAttention)

    prevPacketContext = str(pristinePacketContext[0])
    contextMarkers = []
    contextTimeZones = []
    for i in range(0,countOfRowsAttention):
        if pristinePacketContext[i] != prevPacketContext:
            contextMarkers.append(100)
            contextTimeZones.append(prevPacketContext)
        else:        
            contextMarkers.append(0)
        prevPacketContext = pristinePacketContext[i]
        
        

    experimentBeginTimeAttention = parser.parse(testSubjectAttention["ParseTime"][0])
    experimentBeginTimeMeditation = parser.parse(testSubjectMeditation["ParseTime"][0])

    # Attention
    for i in range(0,countOfRowsAttention):
        currentTime = parser.parse(testSubjectAttention["ParseTime"][i])
        deltaTime = currentTime - experimentBeginTimeAttention
        newDateTime = datetime.strptime(str(deltaTime), "%H:%M:%S")
        minutesFromExperimentBegining = newDateTime.minute + newDateTime.second/60
        testSubjectAttention["ParseTime"][i] = minutesFromExperimentBegining
    
    # Meditation
    for i in range(0,countOfRowsMeditation):
        currentTime = parser.parse(testSubjectMeditation["ParseTime"][i])
        deltaTime = currentTime - experimentBeginTimeMeditation
        newDateTime = datetime.strptime(str(deltaTime), "%H:%M:%S")
        minutesFromExperimentBegining = newDateTime.minute + newDateTime.second/60
        testSubjectMeditation["ParseTime"][i] = minutesFromExperimentBegining
    
    plt.clf()
    plt.plot(testSubjectAttention["ParseTime"],contextMarkers)
    plt.plot(testSubjectAttention["ParseTime"],approxMeditation,label="ESenseMeditation")
    plt.plot(testSubjectAttention["ParseTime"],approxAttention,label="ESenseAttention")
    plt.grid(True)
    titleString = "Испытуемый: " + testSubjectName + '\n' + "Зависимость уровня Esense от времени "
    plt.title(titleString)
    plt.legend()
    # plt.show()
    contextString = ""
    for contex in contextTimeZones:
        contextString += contex[:8] + ";"

    plt.text(0,0,contextString)
    plt.savefig(testSubjectName + "_график")

    with open(F"{testSubjectName}_contexts.txt", "w") as output:
        output.write(str(contextTimeZones))           
 

main()
print("dead")