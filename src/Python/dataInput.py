import logging
import numpy as np
import math
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn

class dataGeneration():

  def __init__(self):
    self.logger = logging.getLogger('logs')
    self.logger.setLevel(logging.NOTSET)
    self.volt = []
    self.amp = []
    self.index = 1
  
  def generateData(self, ampAvg, voltAvg, samples):
    
    if (len(self.volt) == 0):
      self.volt = np.random.normal(loc=voltAvg, scale=(voltAvg/5), size=samples)
      self.amp = np.random.normal(loc=ampAvg, scale=(ampAvg/5), size=samples)
    else:
      self.index += 1
      
      if (self.index == samples):
        lastRead = [self.volt[self.index-1], self.amp[self.index-1]]
        self.volt = []
        self.amp = []
        self.index = 1
        return {"volts":lastRead[0], "amps":lastRead[1]} if (lastRead[0] > 0) else {"volts":0, "amps":0}
    
    self.volt[self.index-1] = self.volt[self.index-1] if (self.volt[self.index-1] > 0) else 0
    self.amp[self.index-1] = self.amp[self.index-1] if (self.amp[self.index-1] > 0) else 0
      
    return {"volts":self.volt[self.index-1], "amps":self.amp[self.index-1]}

class dataRead():
  
  def __init__(self):
    self.logger = logging.getLogger('logs')
    self.logger.setLevel(logging.NOTSET)
    # self.i2c = busio.I2C(board.SCL, board.SDA)
    # self.ads = ADS.ADS1015(self.i2c)
    # self.analIn0 = AnalogIn(self.ads, ADS.P0)
    # self.analIn1 = AnalogIn(self.ads, ADS.P1)
    self.multiplier = 5
  
  def readData(self):
    # volt = self.analIn0.voltage * self.multiplier
    # amp = self.analIn0.voltage * self.multiplier
    # amp = abs(amp - 2.5) 
    # amp = (amp/2.5) * 20
    # return {"volts":volt, "amps":amp]}
    pass
