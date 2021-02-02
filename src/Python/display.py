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
            self.idleScreen.updateText(100, 200, 300, 10, 20, 30, 40)
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
      
    def startActivity(self, data): #? curVoltage, energyPeak
      self.setActivityScreen()
      self.updateActivityRead(data)
      
    def setActivityScreen(self):
      self.setWindowTitle("Activity Screen")
      self.widgetStack.setCurrentWidget(self.activityScreen)
      self.inActivity = True
      
    def updateActivityRead(self, data): #? voltCur, voltPeak
      voltCur = round(float(data.get("voltCur")),2)
      voltPeak = round(float(data.get("voltPeak")),2)
      curDistance = data.get("curDistance")
      actDur = data.get("actDur")
      actDurMin = int(actDur/60)
      actDurSec = int(actDur % 60)
      self.activityScreen.updateText(voltCur, voltPeak, curDistance, actDurMin, actDurSec)
      
    def endActivity(self, time):
      self.setWindowTitle("Transition Screen")
      self.widgetStack.setCurrentWidget(self.transitionScreen)
      self.transitionScreen.startAnimation(time)
      self.inActivity = False
      1
    def scoreActivity(self, activityResults): #? userScore, highScore, energyDay, energyMonth, distance, phonecharge, similarScore, isNewHighScore
      userScore = activityResults.get("userScore")
      highScore = activityResults.get("highScore")
      actDur = activityResults.get("actDur")
      actDurMin = int(actDur/60)
      actDurSec = int(actDur % 60)
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
      self.resultsScreen.updateText(userScore, highScore, actDurMin, actDurSec, distance, phoneCharge, similarScore)
      self.inActivity = False
      
    def setIdleScreen(self, idleScreenData):
      if(not self.inActivity):
        energyDay = idleScreenData.get("energyDay")
        energyMonth = idleScreenData.get("energyMonth")
        highScore = idleScreenData.get("highScore")
        peakVoltage = idleScreenData.get("peakVoltage")
        highestDistance = idleScreenData.get("highestDistance")
        actDur = idleScreenData.get("actDur")
        actDurMin = int(actDur/60)
        actDurSec = int(actDur % 60)

        self.setWindowTitle("Idle Screen")
        self.widgetStack.setCurrentWidget(self.idleScreen)
        self.idleScreen.updateText(energyDay, energyMonth, highScore, peakVoltage, highestDistance, actDurMin, actDurSec)
        self.idleScreen.startTimer()
        
    def setErrorScreen(self, idleScreenData):
      energyDay = idleScreenData.get("energyDay")
      energyMonth = idleScreenData.get("energyMonth")
      highScore = idleScreenData.get("highScore")
      peakVoltage = idleScreenData.get("peakVoltage")
      highestDistance = idleScreenData.get("highestDistance")
      actDur = idleScreenData.get("actDur")
      actDurMin = int(actDur/60)
      actDurSec = int(actDur % 60)
      self.setWindowTitle("Idle Screen Error")
      self.idleScreen.errorScreen()
      self.widgetStack.setCurrentWidget(self.idleScreen)
      self.idleScreen.updateText(energyDay, energyMonth, highScore, peakVoltage, highestDistance, actDurMin, actDurSec)

class idleScreen(QWidget):
  def __init__(self, parent=None):
    super(idleScreen, self).__init__(parent)
    self.setAutoFillBackground(True)
    self.wWidth = 1280
    self.wHeight = 1024
    self.setGeometry(0,0,self.wWidth,self.wHeight)
    self.error = False
    self.imageIndex = 0
    self.timer = QTimer(self)
    self.timer.setInterval(5000)
    self.timer.timeout.connect(self.__changeBackground)
    
    self.resize(self.wWidth, self.wHeight)
    self.bgImage01 = QImage("{0}/img/1_repouso1.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImage01 = self.bgImage01.scaled(self.wWidth, self.wHeight)
    self.bgImage02 = QImage("{0}/img/1_repouso2.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImage02 = self.bgImage02.scaled(self.wWidth, self.wHeight)
    self.bgImage03 = QImage("{0}/img/1_repouso3.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImage03 = self.bgImage03.scaled(self.wWidth, self.wHeight)
    self.bgImageError01 = QImage("{0}/img/6_manutencao1.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageError01 = self.bgImageError01.scaled(self.wWidth, self.wHeight)
    self.bgImageError02 = QImage("{0}/img/6_manutencao2.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageError02 = self.bgImageError02.scaled(self.wWidth, self.wHeight)
    self.bgImageError03 = QImage("{0}/img/6_manutencao3.png".format(pathlib.Path(__file__).parent.absolute()))
    self.bgImageError03 = self.bgImageError03.scaled(self.wWidth, self.wHeight)
    self.customPalette = QPalette()
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImage01))                        
    self.setPalette(self.customPalette)
    
    self.__setText()
    
  def __setText(self):
    self.enDayLabel = QLabel("100", self)
    self.enMonthLabel = QLabel("200", self)
    self.highScoreLabel = QLabel("300", self)
    self.peakVoltage = QLabel("400", self)
    self.highestDistance = QLabel("500", self)
    self.actDurMin = QLabel("60", self)
    self.actDurSec = QLabel("70", self)
    self.enDayLabel.setFixedSize(int(self.wWidth/6), int(self.wHeight/19.6))
    self.enMonthLabel.setFixedSize(int(self.wWidth/6), int(self.wHeight/19.6))
    self.highScoreLabel.setFixedSize(int(self.wWidth/5.5), int(self.wHeight/16.1))
    self.peakVoltage.setFixedSize(int(self.wWidth/5.5), int(self.wHeight/16.1))
    self.highestDistance.setFixedSize(int(self.wWidth/5.5), int(self.wHeight/16.1))
    self.actDurMin.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))
    self.actDurSec.setFixedSize(int(self.wWidth/8), int(self.wHeight/19.6))

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(36)
    self.enDayLabel.setFont(font)
    font.setPointSize(36)
    self.enMonthLabel.setFont(font)
    font.setPointSize(59)
    self.highScoreLabel.setFont(font)
    self.peakVoltage.setFont(font)
    self.highestDistance.setFont(font)
    font.setPointSize(21)
    self.actDurMin.setFont(font)
    self.actDurSec.setFont(font)
    
    self.enDayLabel.setStyleSheet("background-color: transparent")
    self.enMonthLabel.setStyleSheet("background-color: transparent")
    self.highScoreLabel.setStyleSheet("background-color: transparent")
    self.peakVoltage.setStyleSheet("background-color: transparent")
    self.highestDistance.setStyleSheet("background-color: transparent")
    self.actDurMin.setStyleSheet("background-color: transparent")
    self.actDurSec.setStyleSheet("background-color: transparent")
    self.enDayLabel.setAlignment(Qt.AlignRight)
    self.enMonthLabel.setAlignment(Qt.AlignRight)
    self.highScoreLabel.setAlignment(Qt.AlignRight)
    self.peakVoltage.setAlignment(Qt.AlignRight)
    self.highestDistance.setAlignment(Qt.AlignRight)
    self.actDurMin.setAlignment(Qt.AlignRight)
    self.actDurSec.setAlignment(Qt.AlignRight)
    
    
    self.enDayLabel.move(917,264)
    self.enMonthLabel.move(987,506)
    self.highScoreLabel.move(865,850)
    self.peakVoltage.move(915,850)
    self.highestDistance.move(915,850)
    self.actDurMin.move(869,930)
    self.actDurSec.move(931,930)
  
  def updateText(self, energyDay, energyMonth, highScore, peakVoltage, highestDistance, actDurMin, actDurSec):
    self.enDayLabel.setText("{0}".format(energyDay))
    self.enMonthLabel.setText("{0}".format(energyMonth))
    self.highScoreLabel.setText("{0}".format(highScore))
    self.peakVoltage.setText("{0}".format(peakVoltage))
    self.highestDistance.setText("{0}".format(round(highestDistance, 2)))
    self.actDurMin.setText("{0}".format(actDurMin))
    self.actDurSec.setText("{0}".format(actDurSec))

  def errorScreen(self):
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageError))                        
    self.setPalette(self.customPalette)
    self.error = True
    
  def startTimer(self):
    self.timer.start()
    self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImage01))
    self.setPalette(self.customPalette)
    self.highScoreLabel.setVisible(True)
    self.peakVoltage.setVisible(False)
    self.highestDistance.setVisible(False) 
    self.actDurMin.setVisible(False)
    self.actDurSec.setVisible(False)
  
  def stopTimer(self):
    self.timer.stop()
  
  def __changeBackground(self):
    self.imageIndex += 1
    self.imageIndex = self.imageIndex % 3
    if(not self.error):
      if(self.imageIndex == 0):
        self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImage01)) 
        self.highScoreLabel.setVisible(True)
        self.peakVoltage.setVisible(False)
        self.highestDistance.setVisible(False) 
        self.actDurMin.setVisible(False)
        self.actDurSec.setVisible(False)
      elif(self.imageIndex == 1):
        self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImage02)) 
        self.highScoreLabel.setVisible(False)
        self.peakVoltage.setVisible(True)
        self.highestDistance.setVisible(False) 
        self.actDurMin.setVisible(False)
        self.actDurSec.setVisible(False)
      elif(self.imageIndex == 2):
        self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImage03)) 
        self.highScoreLabel.setVisible(False)
        self.peakVoltage.setVisible(False)
        self.highestDistance.setVisible(True) 
        self.actDurMin.setVisible(True)
        self.actDurSec.setVisible(True)
    else:
      if(self.imageIndex == 0):
        self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageError01)) 
        self.highScoreLabel.setVisible(True)
        self.peakVoltage.setVisible(False)
        self.highestDistance.setVisible(False) 
        self.actDurMin.setVisible(False)
        self.actDurSec.setVisible(False)
      elif(self.imageIndex == 1):
        self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageError02)) 
        self.highScoreLabel.setVisible(False)
        self.peakVoltage.setVisible(True)
        self.highestDistance.setVisible(False) 
        self.actDurMin.setVisible(False)
        self.actDurSec.setVisible(False)
      elif(self.imageIndex == 2):
        self.customPalette.setBrush(QPalette.Window, QBrush(self.bgImageError03)) 
        self.highScoreLabel.setVisible(False)
        self.peakVoltage.setVisible(False)
        self.highestDistance.setVisible(True) 
        self.actDurMin.setVisible(True)
        self.actDurSec.setVisible(True)
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
    self.curVoltage = QLabel("100", self)
    self.peakVoltage = QLabel("200", self)
    self.curDistance = QLabel("300", self)
    self.actDurMin = QLabel("400", self)
    self.actDurSec = QLabel("500", self)

    self.curVoltage.setFixedSize(int(self.wWidth/6), int(self.wHeight/16.6))    #[250,50]
    self.peakVoltage.setFixedSize(int(self.wWidth/6), int(self.wHeight/13.1))   #[250,50]
    self.curDistance.setFixedSize(int(self.wWidth/4), int(self.wHeight/13.1))   #[250,50]
    self.actDurMin.setFixedSize(int(self.wWidth/6), int(self.wHeight/13.1))   #[250,50]
    self.actDurSec.setFixedSize(int(self.wWidth/6), int(self.wHeight/13.1))   #[250,50]

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(59)
    self.curVoltage.setFont(font)
    font.setPointSize(40)
    self.peakVoltage.setFont(font)
    font.setPointSize(60)
    self.curDistance.setFont(font)
    font.setPointSize(30)
    self.actDurMin.setFont(font)
    self.actDurSec.setFont(font)
    
    self.curVoltage.setStyleSheet("background-color: transparent")
    self.peakVoltage.setStyleSheet("background-color: transparent")
    self.curDistance.setStyleSheet("background-color: transparent")
    self.actDurMin.setStyleSheet("background-color: transparent")
    self.actDurSec.setStyleSheet("background-color: transparent")
    self.curVoltage.setAlignment(Qt.AlignRight)
    self.peakVoltage.setAlignment(Qt.AlignRight)
    self.curDistance.setAlignment(Qt.AlignRight)
    self.actDurMin.setAlignment(Qt.AlignRight)
    self.actDurSec.setAlignment(Qt.AlignRight)
    
    self.curVoltage.move(865,274)
    self.peakVoltage.move(537,930)
    self.curDistance.move(45,868)
    self.actDurMin.move(635,470)
    self.actDurSec.move(735,470)
  
  def updateText(self, curVoltage, bestScore, curDistance, actDurMin, actDurSec):
    self.curVoltage.setText("{0}".format(curVoltage))
    self.peakVoltage.setText("{0}".format(bestScore))
    self.curDistance.setText("{0}".format(round(curDistance, 2)))
    self.actDurMin.setText("{0}".format(actDurMin))
    self.actDurSec.setText("{0}".format(actDurSec))

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
    self.actDurMin = QLabel("30", self )
    self.actDurSec = QLabel("40", self)
    self.distanceLabel = QLabel("5000", self)
    self.percUsers = QLabel("600", self)
    self.percBattery = QLabel("99", self)

    self.userScoreLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/18.1))
    self.highScoreLabel.setFixedSize(int(self.wWidth/8), int(self.wHeight/18.6))
    self.actDurMin.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.5))
    self.actDurSec.setFixedSize(int(self.wWidth/10), int(self.wHeight/22.6))
    self.distanceLabel.setFixedSize(int(self.wWidth/6), int(self.wHeight/19.1))
    self.percUsers.setFixedSize(int(self.wWidth/12), int(self.wHeight/34.6))
    self.percBattery.setFixedSize(int(self.wWidth/12), int(self.wHeight/34.6))  

    font = QFont("Praktika Rounded Bold")
    font.setBold(True)
    font.setPointSize(53)
    self.userScoreLabel.setFont(font)
    font.setPointSize(45)
    self.highScoreLabel.setFont(font)
    font.setPointSize(24)
    self.actDurMin.setFont(font)
    self.actDurSec.setFont(font)
    font.setPointSize(45)
    self.distanceLabel.setFont(font)
    font.setPointSize(24)
    self.percUsers.setFont(font)
    font.setPointSize(23)
    self.percBattery.setFont(font)
    
    self.userScoreLabel.setStyleSheet("background-color: transparent")
    self.highScoreLabel.setStyleSheet("background-color: transparent")
    self.actDurMin.setStyleSheet("background-color: transparent")
    self.actDurSec.setStyleSheet("background-color: transparent")
    self.distanceLabel.setStyleSheet("background-color: transparent")
    self.percUsers.setStyleSheet("background-color: transparent")
    self.percBattery.setStyleSheet("background-color: transparent")
    self.userScoreLabel.setAlignment(Qt.AlignRight)
    self.highScoreLabel.setAlignment(Qt.AlignRight)
    self.actDurMin.setAlignment(Qt.AlignRight)
    self.actDurSec.setAlignment(Qt.AlignRight)
    self.distanceLabel.setAlignment(Qt.AlignRight)
    self.percUsers.setAlignment(Qt.AlignRight)
    self.percBattery.setAlignment(Qt.AlignRight)
    
    self.userScoreLabel.move(1035,417)
    self.highScoreLabel.move(1005,910)
    self.actDurMin.move(378,935)
    self.actDurSec.move(450,935)
    self.distanceLabel.move(5,897)
    self.percUsers.move(263,515)
    self.percBattery.move(601,650)
  
  def updateText(self, userScore, highScore, actDurMin, actDurSec, distance, percBattery, percUsers):
    self.userScoreLabel.setText("{0}".format(userScore))
    self.highScoreLabel.setText("{0}".format(highScore))
    self.actDurMin.setText("{0}".format(actDurMin))
    self.actDurSec.setText("{0}".format(actDurSec))
    self.distanceLabel.setText("{0}".format(round(distance, 2)))
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
