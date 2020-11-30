import logging
import numpy as np

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
  
  def readData(self):
    pass
