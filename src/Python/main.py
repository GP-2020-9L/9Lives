from datetime import datetime
from threading import Timer
from sys import *
import time
import logging
import traceback
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from dbAcess import *
from display import *
from dataInput import *

if __name__ == "__main__":
  # main()
  logger = logging.getLogger('logs')
  logger.setLevel(logging.NOTSET)
  logging.basicConfig(filename='bike.log', format="%(asctime)s - %(levelname)s : %(message)s", level=logging.NOTSET)
  # self.logger.disabled = True #? Uncomment to disable all logging
  
  app = QApplication(argv)
  window = displayClass()
  window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask)# | Qt.FramelessWindowHint)
  # window.showFullScreen()
  window.setFixedWidth(1280)
  window.setFixedHeight(1024)
  window.show()
  exit(app.exec_())

class dataThread(QThread):
  
  startActivity = pyqtSignal(object)
  updateActivityRead = pyqtSignal(object)
  endActivity = pyqtSignal(object)
  scoreActivity = pyqtSignal(object)
  idleScreen = pyqtSignal(object)
  errorScreen = pyqtSignal(object)

  def __init__(self):
    QThread.__init__(self)
    self.processingData = False
    self.hasError = False
    
    self.logger = logging.getLogger('logs')
    try:
      self.database = dbAccess()
    except(BaseException) as error:
      print(error)
      self.logger.critical('dataThread - __init__ -> {0}'.format(error))
      self.hasError = True

    self.restLimit = 2         #? Amount of time that is possible to rest before activity is ended
    self.readInterval = 0.25   #? Intervals between each read
    self.numGroups = 10        #? Number of groups to determine the percentage of players with similar score
    self.scoreScreenTime = 20  #? Amount of time the results screen displays
    self.metersPerVoltPerSecond = 1.33
    
    self.highScore = 0
    self.energyDay = 0
    self.energyMonth = 0
    self.peakVoltage = 0
    self.highestDistance = 0
    
    self.idleTimer = Timer(self.scoreScreenTime, self.__resetActivity)

    if __debug__: 
      self.logger.info("dataThread -> Starting as data simulation")
      self.dataSource = dataGeneration()
      
    else:
      self.logger.info("dataThread -> Starting as sensor reading")
      self.dataSource = dataRead()
      
    
      
  def run(self):
    self.highScore = round(self.database.getBestScore(),1)
    self.energyDay = round(self.database.getEnergyDay(),1)
    self.energyMonth = round(self.database.getEnergyMonth(),1)
    self.peakVoltage = round(self.database.getPeakVoltage(),1)
    self.highestDistance = self.database.getHighestDistance()
    self.actDur = self.highestDistance[1]
    self.highestDistance = round((self.highestDistance[0] * self.metersPerVoltPerSecond)/1000, 4)
    self.idleScreen.emit({"highScore":self.highScore, "energyDay":self.energyDay, "energyMonth":self.energyMonth, 
                          "peakVoltage": self.peakVoltage, "highestDistance": self.highestDistance, "actDur": self.actDur})
    
    activityStartTime = 0
    activityStopTime = 0
    activityEndedTime = 0
    energyGenerated = 0
    voltPeak = 0
    ampSum = 0
    voltSum = 0
    valuesRead = 0
    
    while(True):
      if(not self.processingData and not self.hasError):
        try:
          if __debug__:
            ampAvg = 0
            voltAvg = 0
            duration = 0
            
            self.logger.info("dataThread - simulation -> Waiting for user input")
            ampAvg, voltAvg, duration = map(int, stdin.readline().strip().split())
            self.logger.debug("dataThread - simulation -> ampAvg({0}), voltAvg({1}), time({2})".format(ampAvg,voltAvg,duration))
          
            if self.idleTimer.isAlive():
              self.idleTimer.cancel()
          
            samples = int(duration / self.readInterval)
            activityStartTime = time.time()
            self.logger.debug("dataThread - simulation -> Starting simulation of {0} samples".format(samples))
            
            self.startActivity.emit({"voltCur":0, "voltPeak":0, "curDistance":0, "actDur": 0}) #? signal ui to change to activity screen
            
            for i in range(int(samples)):
              valuesRead = self.dataSource.generateData(ampAvg, voltAvg, samples)
              energyGenerated += (valuesRead.get("volts") * valuesRead.get("amps") * self.readInterval)
              voltSum += valuesRead.get("volts")
              ampSum += valuesRead.get("amps")
              if (valuesRead.get("volts") > voltPeak): 
                voltPeak = valuesRead.get("volts")
              self.updateActivityRead.emit(({"voltCur":valuesRead.get("volts"), "voltPeak":voltPeak, 
                                             "curDistance": round(((voltSum / (1/self.readInterval)) * self.metersPerVoltPerSecond)/1000, 4), 
                                             "actDur": round(time.time()  - activityStartTime, 1)}))
              self.logger.debug("dataThread - simulation -> valuesRead {0} with {1} V".format(i+1,valuesRead))
              time.sleep(self.readInterval)
            activityStopTime = time.time()   
          else: 
            valuesRead = self.dataSource.readData()
            if (valuesRead.get("volts") > 0):
              self.logger.info("dataThread - sensor -> Starting activity, value of {0}".format(valuesRead))
              if(self.idleTimer is not None):
                self.idleTimer.cancel()
                self.idleTimer = None
              if (valuesRead.get("volts") > voltPeak):
                voltPeak = valuesRead.get("volts")
              self.startActivity.emit({"voltCur":0, "voltPeak":0, "curDistance":0, "actDur": 0}) #? signal ui to change to activity screen
              activityStartTime = time.time()
              while(valuesRead.get("volts") > 0 or activityEndedTime < self.restLimit):
                self.updateActivityRead.emit(({"voltCur":valuesRead.get("volts"), "voltPeak":voltPeak, 
                                             "curDistance": round(((voltSum / (1/self.readInterval)) * self.metersPerVoltPerSecond)/1000, 4), 
                                             "actDur": round(time.time()  - activityStartTime, 1)}))
                self.logger.info("dataThread - sensor -> valuesRead of {0}".format(valuesRead))
                if (valuesRead.get("volts") == 0):
                  activityEndedTime = time.time() - activityStartTime
                else:
                  energyGenerated += (valuesRead.get("volts") * valuesRead.get("amps") * self.readInterval)
                  voltSum += valuesRead.get("volts")
                  ampSum += valuesRead.get("amps")
                  if (valuesRead.get("volts") > voltPeak): 
                    voltPeak = valuesRead.get("volts")
                time.sleep(self.readInterval)
                valuesRead = self.dataSource.readData()
            activityStopTime = time.time() - self.restLimit
          if(energyGenerated > 0):

            date = datetime.now()
            duration = round(activityStopTime - activityStartTime, 1)
            energyAvg = round(energyGenerated / (duration * (1/self.readInterval)), 1)
            voltPeak = round(voltPeak, 1)
            
            if __debug__:
              self.logger.debug("dataThread - simulation -> Simulation ended with duration {0}, energyAvg {1} and voltPeak {2}".format(duration, energyAvg, voltPeak))
            else:
              self.logger.debug("dataThread - valuesRead -> Reading ended with duration {0}, energyAvg {1} and voltPeak {2}".format(duration, energyAvg, voltPeak))
              
            isNewHighScore = self.database.isNewHighScore(energyAvg)
            
            self.database.insertNewRide(date, voltSum/(duration * (1/self.readInterval)), ampSum/(duration * (1/self.readInterval)), voltPeak, energyAvg, duration)
            
            calcTime = np.random.normal(3000,500,1)[0]
            self.endActivity.emit(calcTime)
            self.processingData = True

            self.highScore = round(self.database.getBestScore(),1)
            self.energyDay = round(self.database.getEnergyDay(),1)
            self.energyMonth = round(self.database.getEnergyMonth(),1)
            self.peakVoltage = round(self.database.getPeakVoltage(),1)
            self.highestDistance = self.database.getHighestDistance()
            self.actDur = self.highestDistance[1]
            self.highestDistance = round((self.highestDistance[0] * self.metersPerVoltPerSecond)/1000, 4)
            distance = round(((voltSum / (1/self.readInterval)) * self.metersPerVoltPerSecond)/1000, 4)
            phoneCharge = self.__calcBatteryCharge(ampSum, duration)

            increment = self.highScore / self.numGroups
            lowerBoundScore = 0
            upperBoundScore = 0
            while(upperBoundScore < energyAvg):
              upperBoundScore += increment
            lowerBoundScore = upperBoundScore - increment
            
            similarScore = round(self.database.getSimilarScore(lowerBoundScore, upperBoundScore), 1)
            Timer((calcTime+250)/1000, self.__endActivity, (energyAvg, self.highScore, self.energyDay, self.energyMonth, distance, phoneCharge, 
                                                     similarScore, isNewHighScore, self.peakVoltage, self.highestDistance, self.actDur)).start()
            
            activityStartTime = 0
            activityStopTime = 0
            activityEndedTime = 0
            energyGenerated = 0
            voltPeak = 0
            valuesRead = 0 
        except(BaseException) as error:
          print(error)
          traceback.print_exc()
          self.logger.critical('dataThread - mainLoop -> {0}'.format(error))
          self.hasError = True
          errorScreenData = {"highScore": self.highScore, "energyDay":self.energyDay, "energyMonth":self.energyMonth, 
                             "peakVoltage": self.peakVoltage, "highestDistance": self.highestDistance, "actDur": actDur}
          self.errorScreen.emit(errorScreenData)
      else:
        if(self.hasError):
          errorScreenData = {"highScore": self.highScore, "energyDay":self.energyDay, "energyMonth":self.energyMonth, 
                             "peakVoltage": self.peakVoltage, "highestDistance": self.highestDistance, "actDur": actDur}
          self.errorScreen.emit(errorScreenData)
          self.logger.info('dataThread - mainLoop -> Error: sleeping for 100')
          time.sleep(100)
      time.sleep(0.1)

  def __calcBatteryCharge(self, ampSum, duration):
    toCharge = 3500 # average battery size of 3500 mAh 
    avgAmp = (ampSum / duration) / 1000
    # print((avgAmp / toCharge) * 100)
    return round((avgAmp / toCharge) * 100,1)
    # return round(energyGenerated /100,1)

  def __endActivity(self, energyAvg, highScore, energyDay, energyMonth, distance, phoneCharge, similarScore, isNewHighScore, peakVoltage, highestDistance, actDur):
    if(not self.hasError):
      activityResults = {"userScore":energyAvg, "highScore":highScore, "actDur":actDur, 
              "distance":distance, "phoneCharge": phoneCharge, 
              "similarScore": similarScore, "isNewHighScore":isNewHighScore}
      self.scoreActivity.emit(activityResults)

      self.processingData = False
      self.idleTimer = Timer(self.scoreScreenTime, self.__resetActivity, (highScore, energyDay, energyMonth, peakVoltage, highestDistance, actDur))
      self.idleTimer.start()

  def __resetActivity(self, highScore, energyDay, energyMonth, peakVoltage, highestDistance, actDur):
    if(not self.hasError):
      idleScreenData = {"highScore":highScore, "energyDay":energyDay, "energyMonth":energyMonth, 
                        "peakVoltage": peakVoltage, "highestDistance": highestDistance, "actDur": actDur}
      self.idleScreen.emit(idleScreenData) 
