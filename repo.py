import mysql.connector

DEVICE_NAME = "device"

class MySqlRepo:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            user="grafanawrite",
            passwd="grafana",
            host="18.194.96.218",
            auth_plugin='mysql_native_password'
        )


    def store(self, status):
        self.cursor = self.mydb.cursor()
        time = status.time
        self.store_simple("boxlid", status.openness, time)
        self.store_simple("light", status.light, time)
        self.store_simple("rain", status.rain, time)
        self.store_simple("inside_temperature", status.inside_temp, time)
        self.store_simple("humidity", status.inside_humidity, time)
        self.store_simple("outside_temperature", status.outside_temp, time)
        self.store_simple("airpressure", status.outside_pressure, time)
        self.store_simple("height", status.altitude, time)
        self.store_simple("lpg", status.lpg, time)
        self.store_simple("co", status.co, time)
        self.store_simple("smoke", status.smoke, time)
        self.store_simple("weight", status.weight, time)
        for vibration in status.vibrations:
            self.store_vibration(vibration.frequency, vibration.amplitude, time)
        self.store_simple("dominant_frequency", status.dominant_frequency, time)
        self.store_simple("activity", status.activity, time)
        self.cursor.close()
        self.commit()

    def store_simple(self, table_name, value, time):
        sql_statement = "INSERT INTO `makesense2`.`%s` (`value`, `source`, `time`) VALUES ('%s', '%s', '%s');" % \
            (table_name, value, DEVICE_NAME, time)
        self.cursor.execute(sql_statement)

    def store_vibration(self, frequency, amplitude, time):
        sql_statement = "INSERT INTO `makesense2`.`vibration` (`amplitude`, `frequency`, `source`, `time`) VALUES ('%s', '%s', '%s', '%s');" % \
                (amplitude, str(frequency), DEVICE_NAME, time)
        self.cursor.execute(sql_statement)

    def commit(self):
        self.mydb.commit()

    def close(self):
        self.mydb.commit()
