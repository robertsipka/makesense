import mysql.connector
import datetime

DEVICE_NAME = "device"

class Repo:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            user="grafanawrite",
            passwd="grafana",
            host="18.194.96.218",
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.mydb.cursor()

    def store_simple(self, table_name, value, time=datetime.datetime.now()):
        sql_statement = "INSERT INTO `makesense`.`%s` (`value`, `source`, `time`) VALUES ('%s', '%s', '%s');" % \
            (table_name, str(value), DEVICE_NAME, time)
        self.cursor.execute(sql_statement)

    def store_vibration(self, frequency, amplitude, time=datetime.datetime.now()):
        for _ in range(int(amplitude)):
            sql_statement = "INSERT INTO `makesense`.`vibration` (`amplitude`, `frequency`, `source`, `time`) VALUES ('%s', '%s', '%s', '%s');" % \
                (1, frequency, DEVICE_NAME, time)
            self.cursor.execute(sql_statement)

    def close(self):
        self.cursor.close()
        self.mydb.commit()
