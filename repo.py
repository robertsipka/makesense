import mysql.connector
import datetime

DEVICE_NAME = "device"

class MySqlRepo:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            user="grafanawrite",
            passwd="grafana",
            host="18.194.96.218",
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.mydb.cursor()

    def store(self, status):
        self.store_simple("boxlid", status.openness)
        self.store_simple("light", status.light)
        self.store_simple("rain", status.rain)
        self.store_simple("inside_temperature", status.inside_temp)
        self.store_simple("humidity", status.inside_humidity)
        self.store_simple("outside_temperature", status.outside_temp)
        self.store_simple("airpressure", status.outside_pressure)
        self.store_simple("height", status.altitude)
        self.store_simple("lpg", status.lpg)
        self.store_simple("co", status.co)
        self.store_simple("smoke", status.smoke)
        self.store_simple("weight", status.weight)
        for vibration in status.vibrations:
            self.store_vibration(vibration.frequency, vibration.amplitude)
        self.store_simple("dominant_frequency", status.dominant_frequency)
        self.commit()

    def store_simple(self, table_name, value):
        time = datetime.datetime.now()
        sql_statement = "INSERT INTO `makesense`.`%s` (`value`, `source`, `time`) VALUES ('%s', '%s', '%s');" % \
            (table_name, value, DEVICE_NAME, time)
        self.cursor.execute(sql_statement)

    def store_vibration(self, frequency, amplitude):
        time = datetime.datetime.now()
        sql_statement = "INSERT INTO `makesense`.`vibration` (`amplitude`, `frequency`, `source`, `time`) VALUES ('%s', '%s', '%s', '%s');" % \
                (amplitude, str(frequency), DEVICE_NAME, time)
        self.cursor.execute(sql_statement)

    def commit(self):
        self.mydb.commit()

    def close(self):
        self.cursor.close()
        self.mydb.commit()
