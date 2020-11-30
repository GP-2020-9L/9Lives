import logging
import sys
import pathlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from main import dataThread

#! 1280 x 1024
class displayClass(QMainWindow):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.inActivity = False
        
        self.logger = logging.getLogger('logs')
        self.logger.setLevel(logging.NOTSET)
    
        self.setAutoFillBackground(True)
        self.idleScreen = idleScreen(self)
        self.activityScreen = activityScreen(self)
        self.transitionScreen = transitionScreen(self)
        self.resultsScreen = resultsScreen(self)
        
        self.widgetStack = QStackedLayout()
        self.widgetStack.addWidget(self.idleScreen)
        self.widgetStack.addWidget(self.activityScreen)
        self.widgetStack.addWidget(self.transitionScreen)
        self.widgetStack.addWidget(self.resultsScreen)
        self.__startThread()
        
    def __startThread(self):
      self.dataThread = dataThread()
      self.dataThread.beginActivity.connect(self.startActivity)
      self.dataThread.updateReadings.connect(self.updateActivityRead)
      self.dataThread.processResults.connect(self.setTransitionScreen)
      self.dataThread.endActivity.connect(self.endActivity)
      self.dataThread.resetActivity.connect(self.setIdleScreen)
      self.dataThread.start()

    def closeEvent(self, event):
        ret = QMessageBox.question(self, 'Close request', 'Are you sure you want to quit?',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            qApp.quit()
        else:
            event.ignore()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closeEvent(event=event)  # Close application from escape key.  
        if event.key() == Qt.Key_1:
            self.setIdleScreen([0,0,0])
        if event.key() == Qt.Key_2:
            self.setActivityScreen()
        if event.key() == Qt.Key_3:
            self.setTransitionScreen([2000])
        if event.key() == Qt.Key_4:
            self.setResultsScreen()
        if event.key() == Qt.Key_5:
            self.transitionScreen.startAnimation()
        if event.key() == Qt.Key_0:
            self.idleScreen.updateText(10,20,30)
            
    def setIdleScreen(self, data):
      if(not self.inActivity):
        self.setWindowTitle("Idle Screen")
        self.widgetStack.setCurrentWidget(self.idleScreen)
        bestScore = data[0]
        energyDay = data[1]
        energyMonth = data[2]
        self.idleScreen.updateText(energyDay, energyMonth, bestScore)
      # self.show()
      
    def setActivityScreen(self):
      self.setWindowTitle("Activity Screen")
      self.widgetStack.setCurrentWidget(self.activityScreen)
      self.inActivity = True
      
    def setTransitionScreen(self, time):
      self.setWindowTitle("Transition Screen")
      self.widgetStack.setCurrentWidget(self.transitionScreen)
      self.transitionScreen.startAnimation(time[0])
      self.inActivity = False
      
    def setResultsScreen(self):
      self.setWindowTitle("Results Screen")
      self.widgetStack.setCurrentWidget(self.resultsScreen)
      
    def startActivity(self, data): #? curEnergy, energyPeak
      self.setActivityScreen()
      self.updateActivityRead(data)
      
    def updateActivityRead(self, data): #? curEnergy, energyPeak
      curEnergy = round(float(data[0]),2)
      energyPeak = round(float(data[1]),2)
      self.activityScreen.updateText(curEnergy, energyPeak)
      
      
    def endActivity(self, data): #? score, bestScore, energyDay, energyMonth, distance
      score = data[0]
      bestScore = data[1]
      energyDay = data[2]
      energyMonth = data[3]
      distance = data[4]
      self.setWindowTitle("Results Screen")
      self.widgetStack.setCurrentWidget(self.resultsScreen)
      self.resultsScreen.updateText(score, bestScore, energyDay, energyMonth, distance)
    
      
class idleScreen(QWidget):
  def __init__(self, parent=None):
    super(idleScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    self.wWidth = 1280#qApp.primaryScreen().size().width()/2
    self.wHeight = 1024#qApp.primaryScreen().size().height()
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    
    self.resize(self.wWidth, self.wHeight)
    bgImage = QImage("{0}/img/1_repouso.png".format(pathlib.Path(__file__).parent.absolute()))
    bgImage = bgImage.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(bgImage))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.enDayLabel = QLabel("1", self)
    self.enMonthLabel = QLabel("2", self)
    self.bestScrLabel = QLabel("3", self)
    self.enDayLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))
    self.enMonthLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))
    self.bestScrLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/17.1))

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(40)
    self.enDayLabel.setFont(font)
    self.enMonthLabel.setFont(font)
    font.setPointSize(50)
    self.bestScrLabel.setFont(font)
    
    self.enDayLabel.setStyleSheet("background-color: lightgreen")
    self.enMonthLabel.setStyleSheet("background-color: lightgreen")
    self.bestScrLabel.setStyleSheet("background-color: lightgreen")
    self.enDayLabel.setAlignment(Qt.AlignRight)
    self.enMonthLabel.setAlignment(Qt.AlignRight)
    self.bestScrLabel.setAlignment(Qt.AlignRight)
    
    self.enDayLabel.move(836,239)
    self.enMonthLabel.move(1062,239)
    self.bestScrLabel.move(970,875)
  
  def updateText(self, energyDay, energyMonth, bestScore):
    self.enDayLabel.setText("{0}".format(energyDay))
    self.enMonthLabel.setText("{0}".format(energyMonth))
    self.bestScrLabel.setText("{0}".format(bestScore))
    
class activityScreen(QWidget):
  def __init__(self, parent=None):
    super(activityScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    self.wWidth = 1280#qApp.primaryScreen().size().width()/2
    self.wHeight = 1024#qApp.primaryScreen().size().height()
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    
    self.resize(self.wWidth, self.wHeight)
    bgImage = QImage("{0}/img/2_atividade.png".format(pathlib.Path(__file__).parent.absolute()))
    bgImage = bgImage.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(bgImage))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.curEnergy = QLabel("1", self)
    self.bestEnergy = QLabel("2", self)

    self.curEnergy.setFixedSize(int(self.wWidth/8), int(self.wHeight/21.6))    #[250,50]
    self.bestEnergy.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))   #[250,50]

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(40)
    self.curEnergy.setFont(font)
    font.setPointSize(50)
    self.bestEnergy.setFont(font)
    
    self.curEnergy.setStyleSheet("background-color: lightgreen")
    self.bestEnergy.setStyleSheet("background-color: lightgreen")
    self.curEnergy.setAlignment(Qt.AlignRight)
    self.bestEnergy.setAlignment(Qt.AlignRight)
    
    self.curEnergy.move(726,469)
    self.bestEnergy.move(208,922)
  
  def updateText(self, curEnergy, bestScore):
    self.curEnergy.setText("{0}".format(curEnergy))
    self.bestEnergy.setText("{0}".format(bestScore))

class transitionScreen(QWidget):
  def __init__(self, parent=None):
    super(transitionScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    width = 1280#qApp.primaryScreen().size().width()/2
    height = 1024#qApp.primaryScreen().size().height()
    
    self.resize(width, height)
    bgImage = QImage("{0}/img/3_transicao.png".format(pathlib.Path(__file__).parent.absolute()))
    bgImage = bgImage.scaled(width, height)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(bgImage))                        
    self.setPalette(self.customPalette)
    
    aniWid = QLabel("",self)
    aniWid.setFixedSize(150,90)

    font = QFont("Praktika Rounded Medium")
    font.setPointSize(40)
    aniWid.setFont(font)
    
    aniWid.setStyleSheet("image : url({0}/img/bike.png);".format(pathlib.Path(__file__).parent.absolute()))
    # aniImage = QImage("{0}/img/bike.png".format(pathlib.Path(__file__).parent.absolute()))
    # aniImage = aniImage.scaled(150, 90)
    # aniPalette = QPalette()
    # aniPalette.setBrush(QPalette.Window, QBrush(aniImage))                        
    # aniWid.setPalette(aniPalette)
    aniWid.setAlignment(Qt.AlignRight)
    aniWid.move(75,845)
        
    self.anim = QPropertyAnimation(aniWid, b"pos", self)
    self.anim.setDuration(1900)
    self.anim.setStartValue(QPointF(75,845))
    self.anim.setEndValue(QPointF(1085,845))
    
  def startAnimation(self, time):
    self.anim.setDuration(time)
    self.anim.start()
    pass
    

class resultsScreen(QWidget):
  def __init__(self, parent=None):
    super(resultsScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    self.wWidth = 1280#qApp.primaryScreen().size().width()/2
    self.wHeight = 1024#qApp.primaryScreen().size().height()
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    
    self.resize(self.wWidth, self.wHeight)
    self.bgImage = QImage("{0}/img/5_sem_update_pont.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageUpdate = QImage("{0}/img/4_update_pont.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImage = self.bgImage.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImage))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.scoreLabel = QLabel("1", self)
    self.bestScrLabel = QLabel("2", self)
    self.enDayLabel = QLabel("3", self )
    self.enMonthLabel = QLabel("4", self)
    self.distanceLabel = QLabel("5", self)
    self.percUsers = QLabel("6", self)
    self.percBattery = QLabel("7", self)

    self.scoreLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/21.6))    #[250,50]
    self.bestScrLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/21.6))  #[250,50]
    self.enDayLabel.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.6))  #[250,55]
    self.enMonthLabel.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.6))  #[250,55]
    self.distanceLabel.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.6))  #[250,55]
    self.percUsers.setFixedSize(int(self.wWidth/12), int(self.wHeight/25.6))  #[250,55]
    self.percBattery.setFixedSize(int(self.wWidth/12), int(self.wHeight/25.6))  #[250,55]

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(40)
    self.scoreLabel.setFont(font)
    self.bestScrLabel.setFont(font)
    font.setPointSize(30)
    self.enDayLabel.setFont(font)
    self.enMonthLabel.setFont(font)
    self.distanceLabel.setFont(font)
    font.setPointSize(28)
    self.percUsers.setFont(font)
    self.percBattery.setFont(font)
    
    self.scoreLabel.setStyleSheet("background-color: lightgreen")
    self.bestScrLabel.setStyleSheet("background-color: lightgreen")
    self.enDayLabel.setStyleSheet("background-color: lightgreen")
    self.enMonthLabel.setStyleSheet("background-color: lightgreen")
    self.distanceLabel.setStyleSheet("background-color: lightgreen")
    self.percUsers.setStyleSheet("background-color: lightgreen")
    self.percBattery.setStyleSheet("background-color: lightgreen")
    self.scoreLabel.setAlignment(Qt.AlignRight)
    self.bestScrLabel.setAlignment(Qt.AlignRight)
    self.enDayLabel.setAlignment(Qt.AlignRight)
    self.enMonthLabel.setAlignment(Qt.AlignRight)
    self.distanceLabel.setAlignment(Qt.AlignRight)
    self.percUsers.setAlignment(Qt.AlignRight)
    self.percBattery.setAlignment(Qt.AlignRight)
    
    self.scoreLabel.move(1054,427)
    self.bestScrLabel.move(1067,930)
    self.enDayLabel.move(10,927)
    self.enMonthLabel.move(220,927)
    self.distanceLabel.move(400,942)
    self.percUsers.move(292,490)
    self.percBattery.move(310,730)
  
  def updateText(self, score, bestScore, energyDay, energyMonth, distance):
    self.scoreLabel.setText("{0}".format(score))
    self.bestScrLabel.setText("{0}".format(bestScore))
    self.enDayLabel.setText("{0}".format(energyDay))
    self.enMonthLabel.setText("{0}".format(energyMonth))
    self.distanceLabel.setText("{0}".format(distance))
