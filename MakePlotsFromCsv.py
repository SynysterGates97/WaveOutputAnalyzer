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

# Функция запуска процедуры построения графика для файлов
def main():
    if len(meditationFilesNamesList) > 0:
        for meditationFileName in meditationFilesNamesList:
            if IsMeditationFileHaveMateFile(meditationFileName):
                testSubjectName = GetTestSubjectNameFromFile(meditationFileName)
                experimnent = Experiment.Experiment(testSubjectName)    
                experimnent.Plot() 
                experimnent.CalculateZonesMeans()
                experimnent.WriteOutputToCsv()
                

main()
print("Success!")