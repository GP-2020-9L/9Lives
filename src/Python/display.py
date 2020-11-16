import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class display(QMainWindow):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        # self._menu = QMenu()
        # self._menu.addAction("&Quit", qApp.quit, QKeySequence.Quit)

        # self._trayIcon = QSystemTrayIcon(QIcon("./icon.png"), self)
        # self._trayIcon.setContextMenu(self._menu)
        # self._trayIcon.show()

        # This defers the call to open the dialog after the main event loop has started
        # QTimer.singleShot(0, self.setProfile)

    # @pyqtSlot()
    # def setProfile(self):
    #     if QMessageBox.question(self, "Quit?", "Quit?") != QMessageBox.No:
    #         qApp.quit()
    #     self.hide()
    
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

