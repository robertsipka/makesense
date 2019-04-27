from repo import MySqlRepo
import datetime
import random

step = datetime.timedelta(minutes=10)


def generate_datetimes(start_time, end_time):
    current = start_time
    while current <= end_time:
        yield current
        current += step


def random_measurement_value(minimum):
    return (random.randrange(20) + minimum) / 100


def random_temp():
    return 36 + random.randrange(20) / 10


def generate():
    repo = MySqlRepo()
    start_time = datetime.datetime.now() - datetime.timedelta(hours=5)
    end_time = datetime.datetime.now()
    for timestamp in generate_datetimes(start_time, end_time):
        repo.store_simple("temperature", random_temp(), timestamp)
        for frequency in range(20, 100, 20):
            repo.store_vibration(frequency, frequency // 20, timestamp)
    repo.close()


if __name__ == "__main__":
    generate()
