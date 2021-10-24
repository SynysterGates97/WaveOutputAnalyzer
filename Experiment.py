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


class Experiment:
    

    def __init__(self, testSubjectName):

        self.knn = 10 
        self.testSubjectName = testSubjectName
        self.listOfMeditation = []
        self.listOfConcentration = []        
        self.contextMarkers = []
        self.contextTimeZonesStr = []
        self.contextEndCoordinateWithContextIndex = []        
        self.experimentTimeRelative= []
        
        self.entireMean = ()
        self.entireStandartDeviation = ()
        self.contextZonesStandartDeviation = []

        self.contextZonesMean = []
        self.contextZonesMax = []
        self.contextZonesMin = []

        testSubjectMeditation = pd.read_csv(

            self.testSubjectName+r"_meditation.csv", sep=';')

        testSubjectAttention = pd.read_csv(

            self.testSubjectName+r'_attention.csv', sep=';')


        lesserSize = min(len(testSubjectMeditation), len(testSubjectAttention))


        testSubjectMeditation = testSubjectMeditation[0:lesserSize]

        testSubjectAttention = testSubjectAttention[0:lesserSize]


        pristineMeditation = testSubjectMeditation['ESenseMeditation']

        pristineAttention = testSubjectAttention['ESenseAttention']


        testSubjectMeditation['ParseTime'][0]


        countOfRowsMeditation = len(pristineMeditation)

        countOfRowsAttention = len(pristineAttention)


        # Два цикла ниже просто оставляют только время, без даты.

        for i in range(0, countOfRowsMeditation):

            result = re.match(r'^.+? (\d+?:\d+?:\d+?):.+?',

                              testSubjectMeditation['ParseTime'][i])

            onlyTimeString = result.group(1)

            testSubjectMeditation['ParseTime'][i] = onlyTimeString


        for i in range(0, countOfRowsAttention):

            result = re.match(r'^.+? (\d+?:\d+?:\d+?):.+?',

                              testSubjectAttention['ParseTime'][i])

            onlyTimeString = result.group(1)

            testSubjectAttention['ParseTime'][i] = onlyTimeString


        self.listOfMeditation = self.__KnnRegressionApprox(pristineMeditation, self.knn)
        self.listOfConcentration = self.__KnnRegressionApprox(pristineAttention, self.knn)
        
        pristinePacketContext = testSubjectMeditation['PacketContext']

        prevPacketContext = str(pristinePacketContext[0])
        
        contextNumber = 0
        for i in range(0,countOfRowsAttention):

            if pristinePacketContext[i] != prevPacketContext:
                
                self.contextEndCoordinateWithContextIndex.append(
                    (i,contextNumber)
                )
                contextNumber += 1
                self.contextMarkers.append(100)
                self.contextTimeZonesStr.append(prevPacketContext)

                
            else:        
                self.contextMarkers.append(0)
            if i == countOfRowsAttention - 1:
                self.contextTimeZonesStr.append(prevPacketContext)
                
                self.contextEndCoordinateWithContextIndex.append(
                    (i,contextNumber)
                )
                contextNumber += 1

            prevPacketContext = pristinePacketContext[i]

        meditationMean = np.mean(self.listOfMeditation)     #
        attentionMean = np.mean(self.listOfConcentration)   #

        self.entireMean = (meditationMean, attentionMean)

        secondCenterMoments = [0,0]
        for i in range(0,len(self.listOfMeditation)):
            meditationSecondCenterMoment = (self.listOfMeditation[i] - self.entireMean[0])**2
            attentionSecondCenterMoment = (self.listOfConcentration[i] - self.entireMean[1])**2

            secondCenterMoments[0] += meditationSecondCenterMoment
            secondCenterMoments[1] += attentionSecondCenterMoment

        self.entireStandartDeviation = (
            (secondCenterMoments[0]/len(self.listOfMeditation))**0.5,
            (secondCenterMoments[1]/len(self.listOfConcentration))**0.5
            )
        self.contextZonesStandartDeviation = []

        # Пересчёт времени из абс в относит

        experimentBeginTimeAttention = parser.parse(testSubjectAttention["ParseTime"][0])

        experimentBeginTimeMeditation = parser.parse(testSubjectMeditation["ParseTime"][0])

        # Attention

        for i in range(0,countOfRowsAttention):

            currentTime = parser.parse(testSubjectAttention["ParseTime"][i])

            deltaTime = currentTime - experimentBeginTimeAttention

            newDateTime = datetime.strptime(str(deltaTime), "%H:%M:%S")

            minutesFromExperimentBegining = newDateTime.minute + newDateTime.second/60

            self.experimentTimeRelative.append(minutesFromExperimentBegining)

            # experimentTimeAttList["ParseTime"][i] = minutesFromExperimentBegining
        

        # Meditation

        for i in range(0,countOfRowsMeditation):

            currentTime = parser.parse(testSubjectMeditation["ParseTime"][i])

            deltaTime = currentTime - experimentBeginTimeMeditation

            newDateTime = datetime.strptime(str(deltaTime), "%H:%M:%S")

            minutesFromExperimentBegining = newDateTime.minute + newDateTime.second/60

            # testSubjectMeditation["ParseTime"][i] = minutesFromExperimentBegining


    def __KnnRegressionApprox(self, listOfESenseValues, knn):

        listSize = len(listOfESenseValues)

        delta = int(knn/2)

        leftApproxBorder = delta

        rightApproxBorder = listSize - delta

        #Обработка нулевых данных

        for i in range(listSize):

            if listOfESenseValues[i] == 0:

                for replaceValue in listOfESenseValues[i:]:

                    if replaceValue != 0:

                        listOfESenseValues[i] = replaceValue

                        print(i, replaceValue)

                        break


        approxdList = listOfESenseValues


        #Усреднение методом ближайших соседей

        for i in range(0, listSize):

            currentMean = 0

            if i < leftApproxBorder:

                currentMean = matStat.mean(

                    listOfESenseValues[i:i+int(delta/2)])

            elif i >= rightApproxBorder:

                currentMean = matStat.mean(

                    listOfESenseValues[i-int(delta/2):i])

            else:

                currentMean = matStat.mean(listOfESenseValues[i-delta:i+delta])


            approxdList[i] = int(currentMean)


        return approxdList

    def CalculateZonesMeans(self):
        contextZoneCount = len(self.contextEndCoordinateWithContextIndex)

        for i in range(0, contextZoneCount):
            endOfZone = 0
            beginOfZone = 0

            if i == 0:
                endOfZone = self.contextEndCoordinateWithContextIndex[i][0]
                beginOfZone = 0
            else:
                endOfZone = self.contextEndCoordinateWithContextIndex[i][0]
                beginOfZone = self.contextEndCoordinateWithContextIndex[i - 1][0]

            meditationCut = self.listOfMeditation[beginOfZone:endOfZone]
            attentionCut = self.listOfConcentration[beginOfZone:endOfZone]
            
            self.contextZonesMean.append((np.mean(meditationCut),np.mean(attentionCut)))
            self.contextZonesMax.append((np.max(meditationCut),np.max(attentionCut)))
            self.contextZonesMin.append((np.min(meditationCut),np.min(attentionCut)))

        print(self.contextZonesMean)

        # for endCoordinateContext in self.contextEndCoordinateWithContextIndex:
        #     if endCoordinateContext[1] == 0:
        #         endOfZone = endCoordinateContext[0]

        #         meditationCut = meditationZonesMean[0:endOfZone]
        #         attentionCut = attentionZonesMean[0:endOfZone]

        #         meditationZonesMean.append(np.mean(meditationCut))
        #         attentionZonesMean.append(np.mean(attentionCut))
        #     else:
        #         endOfZone = endCoordinateContext[0]

        #         meditationCut = meditationZonesMean[0:endOfZone]
        #         attentionCut = attentionZonesMean[0:endOfZone]

        #         meditationZonesMean.append(np.mean(meditationCut))
        #         attentionZonesMean.append(np.mean(attentionCut))




        
    def Plot(self):

        plt.clf()

        plt.plot(self.experimentTimeRelative,self.contextMarkers)

        plt.plot(self.experimentTimeRelative,self.listOfMeditation,label="ESenseMeditation")

        plt.plot(self.experimentTimeRelative,self.listOfConcentration,label="ESenseAttention")

        plt.grid(True)

        titleString = "Испытуемый: " + self.testSubjectName + '\n' + "Зависимость уровня Esense от времени "

        plt.title(titleString)

        plt.legend()

        # plt.show()

        contextString = ""

        for contex in self.contextTimeZonesStr:

            contextString += contex[:8] + ";"


        plt.text(0,0,contextString)

        plt.savefig(self.testSubjectName + "_график")


        with open(F"{self.testSubjectName}_contexts.txt", "w") as output:

            output.write(str(self.contextTimeZonesStr))



