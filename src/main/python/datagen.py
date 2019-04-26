import mysql.connector
import datetime
import random

def create_humidity_measurement_sql(device_name, value, time):
    return "INSERT INTO `makesense`.`humidity` (`value`, `source`, `time`) VALUES ('%s', '%s', '%s');" %\
        (str(value), device_name, time)

def create_temperature_measurement_sql(device_name, value, time):
    return "INSERT INTO `makesense`.`temperature` (`value`, `source`, `time`) VALUES ('%s', '%s', '%s');" %\
        (str(value), device_name, time)

def create_vibration_measurement_sql(device_name, frequency, amplitude, time):
    return "INSERT INTO `makesense`.`vibration` (`source`, `frequency`, `amplitude`, `time`) VALUES ('%s', '%s', '%s', '%s');" %\
        (device_name, str(frequency), str(amplitude),time)

def add_vibration_measurement(cursor, device_name, timestamp):

    for frequency in range(20, 100, 20):        
        amplitude = frequency * 2    
        for _ in range(amplitude):
            sql_command = create_vibration_measurement_sql(device_name, frequency, 1, timestamp)
            cursor.execute(sql_command)


step = datetime.timedelta(minutes=10)
def generate_datetimes(start_time, end_time):
    current = start_time
    while current <= end_time:
        yield current
        current += step

device_name = "device_" + str(random.randrange(10000))

def random_measurement_value(minimum):
    return (random.randrange(20) + minimum) / 100

def random_temp():
    return 36 + random.randrange(20) / 10

def generate():
    mydb = mysql.connector.connect(
      user="root",
      passwd="root",
      host="localhost",
      auth_plugin='mysql_native_password'
    )
    cursor = mydb.cursor()

    start_time = datetime.datetime.now() - datetime.timedelta(hours=5)
    end_time = datetime.datetime.now()
    minimum_humidity = random.randrange(40)
    for timestamp in generate_datetimes(start_time, end_time):
        sql_command = create_temperature_measurement_sql(device_name, random_temp(), timestamp)
        cursor.execute(sql_command)
        add_vibration_measurement(cursor, device_name, timestamp)
        
    cursor.close()
    mydb.commit()

generate()
