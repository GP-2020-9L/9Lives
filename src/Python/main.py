from sys import *
import time
import logging
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from Python.dataInput import dataGeneration, dataRead
from dbAcess import *
from display import *
from dataInput import *
from threading import Timer
import numpy as np

if __name__ == "__main__":
  # main()
  logger = logging.getLogger('logs')
  logger.setLevel(logging.NOTSET)
  logging.basicConfig(filename='bike.log', format="%(asctime)s - %(levelname)s : %(message)s", level=logging.NOTSET)
  # self.logger.disabled = True #? Uncomment to disable all logging
  
  app = QApplication(argv)
  window = displayClass()
  window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask) #| Qt.FramelessWindowHint)
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
    
    self.database = dbAccess()
    self.restLimit = 2 # amount of time that is possible to stop before activity is ended
    self.readTime = 0.25
    
    self.highScore = 0
    self.energyDay = 0
    self.energyMonth = 0

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

    self.idleScreen.emit({"highScore":self.highScore, "energyDay":self.energyDay, "energyMonth":self.energyMonth})
    
    activityStartTime = 0
    activityStopTime = 0
    activityEndedTime = 0
    generatedPower = 0
    energyPeak = 0
    energyRead = 0
    
    while(True):
      
      if(not self.processingData and not self.hasError):
        try:
          
          if __debug__:
            avg = 0
            std = 0
            duration = 0
            
            self.logger.info("dataThread - simulation -> Waiting for user input")
            avg, std, duration = map(int, sys.stdin.readline().strip().split())
            self.logger.debug("dataThread - simulation -> Avg({0}), Std({1}), time({2})".format(avg,std,duration))
          
            samples = int(duration / self.readTime)
            activityStartTime = time.time()
            self.logger.debug("dataThread - simulation -> Starting simulation of {0} samples".format(samples))
            
            self.startActivity.emit({"curEnergy":0, "energyPeak":0}) #? signal ui to change to activity screen
            
            for i in range(int(samples)):
              energyRead = self.dataSource.generateData(avg, std, samples)
              generatedPower += energyRead
              if (energyRead > energyPeak): 
                energyPeak = energyRead 
              self.updateActivityRead.emit(({"curEnergy":energyRead, "energyPeak":energyPeak}))
              self.logger.debug("dataThread - simulation -> energyRead {0} with {1} V".format(i+1,energyRead))
              time.sleep(self.readTime)
              
            activityStopTime = time.time()   
          else:
            energyRead = self.dataSource.readData()
            if (energyRead > 0):
              # self.beginActivity.emit() #? signal ui to change to activity screen
              activityStartTime = time.time()
              if (energyRead > energyPeak): energyPeak = energyRead 
              
              while(energyRead > 0 or activityEndedTime > self.restLimit):
                if (energyRead == 0):
                  if(activityStopTime != 0):
                    activityEndedTime = time.time() - activityStopTime
                  else:
                    activityStopTime = time.time()
                else:
                  # self.updateReadings.emit()
                  generatedPower += energyRead
                  if (energyRead > energyPeak): energyPeak = energyRead 
                  
                time.sleep(self.readTime)
                energyRead = self.dataSource.readData()

              # self.endActivity.emit()
        
          if(generatedPower > 0):

            date = datetime.now()
            duration = round(activityStopTime - activityStartTime, 1)
            energyAvg = round(generatedPower / (duration * (1/self.readTime)), 1)
            energyPeak = round(energyPeak, 1)
            
            if __debug__:
              self.logger.debug("dataThread - simulation -> Simulation ended with duration {0}, energyAvg {1} and energyPeak {2}".format(duration, energyAvg, energyPeak))
            else:
              self.logger.debug("dataThread - energyRead -> Reading ended with duration {0}, energyAvg {1} and energyPeak {2}".format(duration, energyAvg, energyPeak))
              
            isNewHighScore = self.database.isNewHighScore(energyAvg)
            
            self.database.insertNewRide(date, energyAvg, energyPeak, duration)
            
            # todo random number between 1500 and 3000 ms for random calc time 
            
            self.endActivity.emit(np.random.normal(2250,200,1)[0])
            self.processingData = True

            self.highScore = round(self.database.getBestScore(),1)
            self.energyDay = round(self.database.getEnergyDay(),1)
            self.energyMonth = round(self.database.getEnergyMonth(),1)
            distance = 0.25 # todo kekw do this :)
            phoneCharge = 1
            similarScore = 10
            
            # todo % users with similar result
            # todo % of phone battery charged
            # todo check if new highscore


            Timer(2, self.__endActivity, (energyAvg, self.highScore, self.energyDay, self.energyMonth, distance, phoneCharge, similarScore, isNewHighScore)).start()
            
            activityStartTime = 0
            activityStopTime = 0
            activityEndedTime = 0
            generatedPower = 0
            energyPeak = 0
            energyRead = 0 
        except(BaseException) as error:
          print(error.with_traceback())
          self.logger.critical('dataThread - mainLoop -> {0}'.format(error.with_traceback()))
          self.hasError = True
          
      else:
        self.logger.info('dataThread - mainLoop -> Sleeping for 100')
        time.sleep(100)
      time.sleep(0.1)


  def __endActivity(self, energyAvg, highScore, energyDay, energyMonth, distance, phoneCharge, similarScore, isNewHighScore):
    if(not self.hasError):
      activityResults = {"userScore":energyAvg, "highScore":highScore, "energyDay":energyDay, 
              "energyMonth":energyMonth, "distance":distance, "phoneCharge": phoneCharge, 
              "similarScore": similarScore, "isNewHighScore":isNewHighScore}
      self.scoreActivity.emit(activityResults)

      Timer(5, self.__resetActivity, (highScore, energyDay, energyMonth)).start()
      self.processingData = False

  def __resetActivity(self, highScore, energyDay, energyMonth):
    if(not self.hasError):
      idleScreenData = {"highScore":highScore, 
                    "energyDay":energyDay,
                    "energyMonth":energyMonth}
      self.idleScreen.emit(idleScreenData) 
