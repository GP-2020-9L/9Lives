from sys import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from display import display


class main():
  def __init__(self):
    self.app = QApplication(argv)
    self.window = display()
    self.window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask) # | Qt.FramelessWindowHint)
    self.window.showFullScreen()
    self.window.show()
    exit(self.app.exec_())






if __name__ == "__main__":
  # main()
  app = QApplication(argv)
  window = display()
  window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask) # | Qt.FramelessWindowHint)
  window.showFullScreen()
  window.show()
  exit(app.exec_())

