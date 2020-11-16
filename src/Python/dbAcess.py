import psycopg2

class dbAccess():
  """
  This class is responsible for all accesses to the database
  """
  def __init__(self, conn):
    
    params = __config(self)
    conn = psycopg2.connect(**params)
    
    
  def __config(self, filename='../Database/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


  def insertNewRide(self, rideData):
    try:
      cur = self.conn.cursor()
      
      cur.execute("""INSERT into public.bike( ...
                    date, energyAvg, energyPeak, duration)
                    values ({1}, {2}, {3}, {4});""".format(
                      rideData[0], rideData[1], rideData[2], rideData[3]))
      cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


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
        print(error)
    finally:
        if self.conn is not None:
            self.conn.close()

    return isHighestScore
  
  
