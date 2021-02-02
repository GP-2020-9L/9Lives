import logging
import pathlib
import psycopg2
import configparser
class dbAccess():
  """
  This class is responsible for all accesses to the database
  """
  def __init__(self):
    self.logger = logging.getLogger('logs')
    self.logger.info('dbAccess -> Starting connection to database')
    self.params = self.__config()
    self.NoneType = type(None)
    
    
  def __config(self, filename='/Database/database.ini', section='postgresql'):
    
    file = str(pathlib.Path(__file__).parent.parent.absolute()) + filename
    self.logger.info("dbAccess -> Parsing config file at {0}".format(file))
    
    # create a parser
    parser = configparser.ConfigParser()
    # read config file
    parser.read(file)
    
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
      self.logger.critical('dbAccess -> Section {0} not found in the {1} file'.format(section, filename))
      raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    self.logger.info('dbAccess -> Config file parse completed')
    return db

  def insertNewRide(self, date, voltAvg, ampAvg, voltPeak, score, duration):
    
    self.logger.info('dbAccess - insertNewRide -> Inserting new ride')
    self.logger.debug('dbAccess - insertNewRide -> Ride on {0} with duration {1}, voltAvg {2}, ampAvg {3} and voltPeak {3}'.format(
                      date, duration, voltAvg, ampAvg, voltPeak))
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""INSERT into public.bike(
                    date, voltAvg, ampAvg, voltPeak, score, duration)
                    values (%s, %s, %s, %s, %s, %s);""", 
                    (date, voltAvg, ampAvg, voltPeak, score, duration))
      conn.commit()
      cur.close()
      conn.close()
      self.logger.info('dbAccess - insertNewRide -> Insertion completed')
    except (Exception, psycopg2.DatabaseError) as error:
      self.logger.critical('dbAccess - insertNewRide -> {0}'.format(error))
      raise

  def isNewHighScore(self, rideScore):
    isHighestScore = False
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT max(score)
                    from bike;""")
      
      highScore = cur.fetchone()
      if(type(highScore[0]) is self.NoneType):
        isHighestScore = True
      else:  
        if(rideScore > highScore[0]):
          isHighestScore = True
      cur.close()
      conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
    
    return isHighestScore
  
  def getBestScore(self):
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT max(score)
                    from bike;""")
      
      bestScore = cur.fetchone()
      cur.close()
      conn.close()
      return bestScore[0] if type(bestScore[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
    
  def getPeakVoltage(self):
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT max(voltPeak)
                    from bike;""")
      
      voltPeak = cur.fetchone()
      cur.close()
      conn.close()
      return voltPeak[0] if type(voltPeak[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
  
  def getHighestDistance(self):
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT voltAvg, duration
                    from bike;""")
      
      distances = cur.fetchall()
      cur.close()
      conn.close()
      
      bestDistance = [0,0]
      
      for dt in distances:
        if(dt[0] * dt[1] > bestDistance[0]):
          bestDistance[0] = dt[0] * dt[1]
          bestDistance[1] = dt[1]
      
      return bestDistance
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
    
  def getEnergyDay(self):
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT sum(score * duration)
                    from bike
                    where date(date) = CURRENT_DATE;""")
      energyDay = cur.fetchone()
      cur.close()
      conn.close()
      return energyDay[0] if type(energyDay[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
  
  def getEnergyMonth(self):
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT sum(score * duration)
                    from bike
                    where date_trunc('month',date) = date_trunc('month', CURRENT_DATE);""")
      
      energyMonth = cur.fetchone()
      cur.close()
      conn.close()
      return energyMonth[0] if type(energyMonth[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise  
    
  def getSimilarScore(self, lowerBound, upperBound):
    try:
      conn = psycopg2.connect(**self.params)
      self.logger.info("dbAccess -> Connection to postgres established")
      cur = conn.cursor()
      
      cur.execute("""SELECT count(score)
                    from bike
                    where score >= %s and score <= %s;""", 
                    (lowerBound, upperBound))
      
      numInRange = cur.fetchone()
      cur.execute("""SELECT count(score)
                     from bike""")
      totalReg = cur.fetchone()
      cur.close()
      conn.close()
      
      percUsers = numInRange[0] / totalReg[0]
      return percUsers * 100 if type(percUsers) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise  
    
