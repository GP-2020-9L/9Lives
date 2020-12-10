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
    params = self.__config()
    self.conn = psycopg2.connect(**params)
    self.logger.info("dbAccess -> Connection to postgres established")
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

  def insertNewRide(self, date, energyAvg, energyPeak, duration):
    
    self.logger.info('dbAccess - insertNewRide -> Inserting new ride')
    self.logger.debug('dbAccess - insertNewRide -> Ride on {0} with duration {1}, energyAvg {2} and energyPeak {3}'.format(
                      date, duration, energyAvg, energyPeak))
    try:
      cur = self.conn.cursor()
      
      cur.execute("""INSERT into public.bike(
                    date, energyAvg, energyPeak, duration)
                    values (%s, %s, %s, %s);""", 
                    (date, energyAvg, energyPeak, duration))
      self.conn.commit()
      cur.close()
      
      self.logger.info('dbAccess - insertNewRide -> Insertion completed')
    except (Exception, psycopg2.DatabaseError) as error:
      self.logger.critical('dbAccess - insertNewRide -> {0}'.format(error))
      raise

  def isNewHighScore(self, rideEnergyAvg):
    isHighestScore = False
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT max(energyAvg)
                    from bike;""")
      
      highScore = cur.fetchone()
      if(type(highScore[0]) is self.NoneType):
        isHighestScore = True
      else:  
        if(rideEnergyAvg > highScore[0]):
          isHighestScore = True
      cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
    
    return isHighestScore
  
  def getBestScore(self):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT max(energyAvg)
                    from bike;""")
      
      bestScore = cur.fetchone()
      cur.close()
      return bestScore[0] if type(bestScore[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
  
  def getEnergyDay(self):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT sum(energyAvg * duration)
                    from bike
                    where date(date) = CURRENT_DATE;""")
      energyDay = cur.fetchone()
      cur.close()
      return energyDay[0] if type(energyDay[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise
  
  def getEnergyMonth(self):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT sum(energyAvg * duration)
                    from bike
                    where date_trunc('month',date) = date_trunc('month', CURRENT_DATE);""")
      
      energyMonth = cur.fetchone()
      cur.close()
      return energyMonth[0] if type(energyMonth[0]) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise  
    
  def getSimilarScore(self, lowerBound, upperBound):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT count(energyAvg)
                    from bike
                    where energyAvg >= %s and energyAvg <= %s;""", 
                    (lowerBound, upperBound))
      
      numInRange = cur.fetchone()
      cur.execute("""SELECT count(energyAvg)
                     from bike""")
      totalReg = cur.fetchone()
      cur.close()
      
      percUsers = numInRange[0] / totalReg[0]
      return percUsers * 100 if type(percUsers) is not self.NoneType else 0
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
      raise  
    
