import logging
import numpy as np
# import Adafruit_ADS1x15

class dataGeneration():

  def __init__(self):
    self.logger = logging.getLogger('logs')
    self.logger.setLevel(logging.NOTSET)
    self.data = []
    self.index = 1
  
  def generateData(self, avg, std, samples):
    
    if (len(self.data) == 0):
      self.data = np.random.normal(loc=avg, scale=std, size=samples)
    else:
      self.index += 1
      
      if (self.index == samples):
        lastRead = self.data[self.index-1]
        self.data = []
        self.index = 1
        return lastRead if (lastRead > 0) else 0
    
      
    return self.data[self.index-1] if (self.data[self.index-1] > 0) else 0
    


class dataRead():
  
  def __init__(self):
    self.logger = logging.getLogger('logs')
    self.logger.setLevel(logging.NOTSET)
    # self.adc = Adafruit_ADS1x15.ADS1115()
    self.GAIN = 1
  
  def readData(self):
    # value1 = self.adc.read_adc_difference(0, gain=self.GAIN)
    # value2 = self.adc.read_adc_difference(1, gain=self.GAIN)
    # value3 = self.adc.read_adc_difference(2, gain=self.GAIN)
    # value4 = self.adc.read_adc_difference(3, gain=self.GAIN)
    pass
