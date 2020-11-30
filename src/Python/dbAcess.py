import psycopg2
import configparser
import pathlib
import logging
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

  def isNewHighScore(self, rideEnergyAvg):
    isHighestScore = False
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT max(energyAvg)
                    from bike;""")
      
      highScore = cur.fetchone()
      
      if(rideEnergyAvg > highScore):
        isHighestScore = True
      cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error, " - 1")
    finally:
        if self.conn is not None:
            self.conn.close()

    return isHighestScore
  
  def getBestScore(self):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT max(energyAvg)
                    from bike;""")
      
      bestScore = cur.fetchone()
      cur.close()
      return bestScore if type(bestScore) is None else [0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return 0
  
  def getEnergyDay(self):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT sum(energyAvg * duration)
                    from bike
                    where date(date) = CURRENT_DATE;""")
      energyDay = cur.fetchone()
      cur.close()
      return energyDay if type(energyDay) is None else [0] 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return 0
  
  def getEnergyMonth(self):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""SELECT sum(energyAvg * duration)
                    from bike
                    where date_trunc('month',date) = date_trunc('month', CURRENT_DATE);""")
      
      energyMonth = cur.fetchone()
      cur.close()
      return energyMonth if type(energyMonth) is None else [0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return 0
    
