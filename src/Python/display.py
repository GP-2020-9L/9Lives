import logging
import pathlib
from main import dataThread
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

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
      self.dataThread.startActivity.connect(self.startActivity)
      self.dataThread.updateActivityRead.connect(self.updateActivityRead)
      self.dataThread.endActivity.connect(self.endActivity)
      self.dataThread.scoreActivity.connect(self.scoreActivity)
      self.dataThread.idleScreen.connect(self.setIdleScreen)
      self.dataThread.errorScreen.connect(self.setErrorScreen)
      self.dataThread.start()

    def closeEvent(self, event):
        ret = QMessageBox.question(self, 'Close request', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            qApp.quit()
        else:
            event.ignore()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closeEvent(event=event)  # Close application from escape key.  
        if event.key() == Qt.Key_1:
            self.setWindowTitle("Idle Screen")
            self.widgetStack.setCurrentWidget(self.idleScreen)
            self.idleScreen.updateText(100, 200, 300)
        if event.key() == Qt.Key_2:
            self.setWindowTitle("Activity Screen")
            self.widgetStack.setCurrentWidget(self.activityScreen)
        if event.key() == Qt.Key_3:
            self.setWindowTitle("Transition Screen")  
            self.widgetStack.setCurrentWidget(self.transitionScreen)
            self.transitionScreen.startAnimation(2000)
        if event.key() == Qt.Key_4:
            self.setWindowTitle("Results Screen")
            self.widgetStack.setCurrentWidget(self.resultsScreen)
        if event.key() == Qt.Key_5:
            self.transitionScreen.startAnimation(1500)
      
    def setResultsScreen(self):
      self.setWindowTitle("Results Screen")
      self.widgetStack.setCurrentWidget(self.resultsScreen)
      
    def startActivity(self, data): #? curEnergy, energyPeak
      self.setActivityScreen()
      self.updateActivityRead(data)
      
    def setActivityScreen(self):
      self.setWindowTitle("Activity Screen")
      self.widgetStack.setCurrentWidget(self.activityScreen)
      self.inActivity = True
      
    def updateActivityRead(self, data): #? curEnergy, energyPeak
      curEnergy = round(float(data.get("curEnergy")),2)
      energyPeak = round(float(data.get("energyPeak")),2)
      self.activityScreen.updateText(curEnergy, energyPeak)
      
    def endActivity(self, time):
      self.setWindowTitle("Transition Screen")
      self.widgetStack.setCurrentWidget(self.transitionScreen)
      self.transitionScreen.startAnimation(time)
      self.inActivity = False
      
    def scoreActivity(self, activityResults): #? userScore, highScore, energyDay, energyMonth, distance, phonecharge, similarScore, isNewHighScore
      userScore = activityResults.get("userScore")
      highScore = activityResults.get("highScore")
      energyDay = activityResults.get("energyDay")
      energyMonth = activityResults.get("energyMonth")
      distance = activityResults.get("distance")
      phoneCharge = activityResults.get("phoneCharge")
      similarScore = activityResults.get("similarScore")
      isNewHighScore = activityResults.get("isNewHighScore")
      self.setWindowTitle("Results Screen")
      if(isNewHighScore):
        self.resultsScreen.setUpdatedBg()
      else:
        self.resultsScreen.setStandardBg()
      self.widgetStack.setCurrentWidget(self.resultsScreen)
      self.resultsScreen.updateText(userScore, highScore, energyDay, energyMonth, distance, phoneCharge, similarScore)
      self.inActivity = False
      
    def setIdleScreen(self, idleScreenData):
      if(not self.inActivity):
        highScore = idleScreenData.get("highScore")
        energyDay = idleScreenData.get("energyDay")
        energyMonth = idleScreenData.get("energyMonth")
        self.setWindowTitle("Idle Screen")
        self.widgetStack.setCurrentWidget(self.idleScreen)
        self.idleScreen.updateText(energyDay, energyMonth, highScore)
        
    def setErrorScreen(self, idleScreenData):
      highScore = idleScreenData.get("highScore")
      energyDay = idleScreenData.get("energyDay")
      energyMonth = idleScreenData.get("energyMonth")
      self.setWindowTitle("Idle Screen Error")
      self.idleScreen.errorScreen()
      self.widgetStack.setCurrentWidget(self.idleScreen)
      self.idleScreen.updateText(energyDay, energyMonth, highScore)
class idleScreen(QWidget):
  def __init__(self, parent=None):
    super(idleScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    self.wWidth = 1280
    self.wHeight = 1024
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    
    self.resize(self.wWidth, self.wHeight)
    bgImage = QImage("{0}/img/1_repouso.png".format(pathlib.Path(__file__).parent.absolute()))
    bgImage = bgImage.scaled(self.wWidth, self.wHeight)
    self.bgImageError = QImage("{0}/img/6_manutencao.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageError = self.bgImageError.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(bgImage))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.enDayLabel = QLabel("100", self)
    self.enMonthLabel = QLabel("200", self)
    self.highScoreLabel = QLabel("300", self)
    self.enDayLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))
    self.enMonthLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))
    self.highScoreLabel.setFixedSize(int(self.wWidth/5.5), int(self.wHeight/16.1))

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(45)
    self.enDayLabel.setFont(font)
    font.setPointSize(45)
    self.enMonthLabel.setFont(font)
    font.setPointSize(59)
    self.highScoreLabel.setFont(font)
    
    self.enDayLabel.setStyleSheet("background-color: transparent")
    self.enMonthLabel.setStyleSheet("background-color: transparent")
    self.highScoreLabel.setStyleSheet("background-color: transparent")
    self.enDayLabel.setAlignment(Qt.AlignRight)
    self.enMonthLabel.setAlignment(Qt.AlignRight)
    self.highScoreLabel.setAlignment(Qt.AlignRight)
    
    self.enDayLabel.move(828,230)
    self.enMonthLabel.move(1054,230)
    self.highScoreLabel.move(889,865)
  
  def updateText(self, energyDay, energyMonth, highScore):
    self.enDayLabel.setText("{0}".format(energyDay))
    self.enMonthLabel.setText("{0}".format(energyMonth))
    self.highScoreLabel.setText("{0}".format(highScore))

  def errorScreen(self):
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageError))                        
    self.setPalette(self.customPalette)
    
class activityScreen(QWidget):
  def __init__(self, parent=None):
    super(activityScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    self.wWidth = 1280
    self.wHeight = 1024
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    
    self.resize(self.wWidth, self.wHeight)
    bgImage = QImage("{0}/img/2_atividade.png".format(pathlib.Path(__file__).parent.absolute()))
    bgImage = bgImage.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(bgImage))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.curEnergy = QLabel("100", self)
    self.bestEnergy = QLabel("200", self)

    self.curEnergy.setFixedSize(int(self.wWidth/8), int(self.wHeight/16.6))    #[250,50]
    self.bestEnergy.setFixedSize(int(self.wWidth/6), int(self.wHeight/13.1))   #[250,50]

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(59)
    self.curEnergy.setFont(font)
    font.setPointSize(74)
    self.bestEnergy.setFont(font)
    
    self.curEnergy.setStyleSheet("background-color: transparent")
    self.bestEnergy.setStyleSheet("background-color: transparent")
    self.curEnergy.setAlignment(Qt.AlignRight)
    self.bestEnergy.setAlignment(Qt.AlignRight)
    
    self.curEnergy.move(711,449)
    self.bestEnergy.move(143,898)
  
  def updateText(self, curEnergy, bestScore):
    self.curEnergy.setText("{0}".format(curEnergy))
    self.bestEnergy.setText("{0}".format(bestScore))

class transitionScreen(QWidget):
  def __init__(self, parent=None):
    super(transitionScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    width = 1280
    height = 1024
    
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
    self.wWidth = 1280
    self.wHeight = 1024
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    
    self.resize(self.wWidth, self.wHeight)
    self.bgImageStandard = QImage("{0}/img/5_sem_update_pont.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageUpdate = QImage("{0}/img/4_update_pont.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageStandard = self.bgImageStandard.scaled(self.wWidth, self.wHeight)
    self.bgImageUpdate = self.bgImageUpdate.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageStandard))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.userScoreLabel = QLabel("100", self)
    self.highScoreLabel = QLabel("200", self)
    self.enDayLabel = QLabel("3000", self )
    self.enMonthLabel = QLabel("4000", self)
    self.distanceLabel = QLabel("5000", self)
    self.percUsers = QLabel("600", self)
    self.percBattery = QLabel("700", self)

    self.userScoreLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/18.1))
    self.highScoreLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/18.6))
    self.enDayLabel.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.5))
    self.enMonthLabel.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.6))
    self.distanceLabel.setFixedSize(int(self.wWidth/10), int(self.wHeight/27.6))
    self.percUsers.setFixedSize(int(self.wWidth/12), int(self.wHeight/34.6))
    self.percBattery.setFixedSize(int(self.wWidth/12), int(self.wHeight/34.6))  

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(53)
    self.userScoreLabel.setFont(font)
    self.highScoreLabel.setFont(font)
    font.setPointSize(42)
    self.enDayLabel.setFont(font)
    self.enMonthLabel.setFont(font)
    font.setPointSize(33)
    self.distanceLabel.setFont(font)
    font.setPointSize(24)
    self.percUsers.setFont(font)
    self.percBattery.setFont(font)
    
    self.userScoreLabel.setStyleSheet("background-color: transparent")
    self.highScoreLabel.setStyleSheet("background-color: transparent")
    self.enDayLabel.setStyleSheet("background-color: transparent")
    self.enMonthLabel.setStyleSheet("background-color: transparent")
    self.distanceLabel.setStyleSheet("background-color: transparent")
    self.percUsers.setStyleSheet("background-color: transparent")
    self.percBattery.setStyleSheet("background-color: transparent")
    self.userScoreLabel.setAlignment(Qt.AlignRight)
    self.highScoreLabel.setAlignment(Qt.AlignRight)
    self.enDayLabel.setAlignment(Qt.AlignRight)
    self.enMonthLabel.setAlignment(Qt.AlignRight)
    self.distanceLabel.setAlignment(Qt.AlignRight)
    self.percUsers.setAlignment(Qt.AlignRight)
    self.percBattery.setAlignment(Qt.AlignRight)
    
    self.userScoreLabel.move(1022,417)
    self.highScoreLabel.move(1035,920)
    self.enDayLabel.move(-16,925)
    self.enMonthLabel.move(194,925)
    self.distanceLabel.move(359,948)
    self.percUsers.move(260,497)
    self.percBattery.move(281,739)
  
  def updateText(self, userScore, highScore, energyDay, energyMonth, distance, percBattery, percUsers):
    self.userScoreLabel.setText("{0}".format(userScore))
    self.highScoreLabel.setText("{0}".format(highScore))
    self.enDayLabel.setText("{0}".format(energyDay))
    self.enMonthLabel.setText("{0}".format(energyMonth))
    self.distanceLabel.setText("{0}".format(distance))
    self.percBattery.setText("{0}".format(percBattery))
    self.percUsers.setText("{0}".format(percUsers))
    
  def setStandardBg(self):
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageStandard))        
    self.percUsers.setVisible(True)                
    self.setPalette(self.customPalette)
  
  def setUpdatedBg(self):
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageUpdate))        
    self.percUsers.setVisible(False)                
    self.setPalette(self.customPalette)
