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


# class main():
#   def __init__(self):
#     self.app = QApplication(argv)
#     self.window = display()
#     self.window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask) # | Qt.FramelessWindowHint)
#     self.window.showFullScreen()
#     self.window.show()
#     exit(self.app.exec_())


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
  
  beginActivity = pyqtSignal(object)
  updateReadings = pyqtSignal(object)
  processResults = pyqtSignal()
  endActivity = pyqtSignal(object)
  resetActivity = pyqtSignal(object)

  def __init__(self):
    QThread.__init__(self)
    
    self.logger = logging.getLogger('logs')
    
    self.database = dbAccess()
    self.restLimit = 2 # amount of time that is possible to stop before activity is ended
    self.readTime = 0.25

    if __debug__: 
      self.logger.info("dataThread -> Starting as data simulation")
      self.dataSource = dataGeneration()
      
    else:
      self.logger.info("dataThread -> Starting as sensor reading")
      self.dataSource = dataRead()
      
  def run(self):
    
    bestScore = round(self.database.getBestScore()[0],1)
    energyDay = round(self.database.getEnergyDay()[0],1)
    energyMonth = round(self.database.getEnergyMonth()[0],1)
    
    self.resetActivity.emit([bestScore, energyDay, energyMonth])
    
    activityStartTime = 0
    activityStopTime = 0
    activityEndedTime = 0
    generatedPower = 0
    energyPeak = 0
    read = 0
    
    while(True):
      
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
        
        self.beginActivity.emit([0, 0]) #? signal ui to change to activity screen
        
        for i in range(int(samples)):
          read = self.dataSource.generateData(avg, std, samples)
          generatedPower += read
          if (read > energyPeak): energyPeak = read 
          self.updateReadings.emit(([read, energyPeak]))
          self.logger.debug("dataThread - simulation -> Read {0} with {1} V".format(i+1,read))
          time.sleep(self.readTime)
          
        activityStopTime = time.time()
        
      else:
        read = self.dataSource.readData()
        if (read > 0):
          # self.beginActivity.emit() #? signal ui to change to activity screen
          activityStartTime = time.time()
          if (read > energyPeak): energyPeak = read 
          
          while(read > 0 or activityEndedTime > self.restLimit):
            if (read == 0):
              if(activityStopTime != 0):
                activityEndedTime = time.time() - activityStopTime
              else:
                activityStopTime = time.time()
            else:
              # self.updateReadings.emit()
              generatedPower += read
              if (read > energyPeak): energyPeak = read 
              
            time.sleep(self.readTime)
            read = self.dataSource.readData()

          # self.endActivity.emit()
      
      if(generatedPower > 0):
        
        date = datetime.now()
        duration = round(activityStopTime - activityStartTime, 1)
        energyAvg = round(generatedPower / (duration * (1/self.readTime)), 1)
        energyPeak = round(energyPeak, 1)
        
        if __debug__:
          self.logger.debug("dataThread - simulation -> Simulation ended with duration {0}, energyAvg {1} and energyPeak {2}".format(duration, energyAvg, energyPeak))
        else:
          self.logger.debug("dataThread - read -> Reading ended with duration {0}, energyAvg {1} and energyPeak {2}".format(duration, energyAvg, energyPeak))
          
        self.database.insertNewRide(date, energyAvg, energyPeak, duration)
        self.processResults.emit([1900])
        
        highScore = round(self.database.getBestScore()[0],1)
        energyDay = round(self.database.getEnergyDay()[0],1)
        energyMonth = round(self.database.getEnergyMonth()[0],1)
        distance = 0.25 # todo kekw do this :)

        Timer(2, self.__endActivity, (energyAvg, highScore, energyDay, energyMonth, distance)).start()
        
        # todo check if new highscore
      
      time.sleep(0.1)


  def __endActivity(self, score, bestScore, energyDay, energyMonth, distance):
    self.endActivity.emit([score, bestScore, energyDay, energyMonth, distance])
    Timer(5, self.__resetActivity, (bestScore, energyDay, energyMonth)).start()

  def __resetActivity(self, bestScore, energyDay, energyMonth):
    self.resetActivity.emit([bestScore, energyDay, energyMonth]) 
