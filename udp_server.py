import logging
import socket
import struct
import repo

log = logging.getLogger('udp_server')


def udp_server(host='0.0.0.0', port=1234):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    log.info("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))
    while True:
        (data, addr) = s.recvfrom(128*1024)
        yield data

def get_float(bytes, prec=0):
    return round(struct.unpack('f', bytes)[0], prec)

def get_int(bytes):
    return int.from_bytes(bytes, byteorder="big", signed=True)

class HiveStatus:
    def __init__(self, data):
        self.openness = get_float(data[0:4])
        self.lpg = get_float(data[4:8])
        self.co = get_float(data[8:12])
        self.smoke = get_float(data[12:16])
        self.outside_temp = get_float(data[16:20], 2)
        self.outside_pressure = get_float(data[20:24], 2)
        self.altitude = get_float(data[24:28])
        self.inside_temp = get_float(data[28:32], 2)
        self.inside_humidity = get_float(data[32:36], 2)
        self.rain = get_float(data[36:40])
        self.weight = get_float(data[40:44], 2)
        self.light = get_float(data[44:48])
        self.dominant_frequency = get_float(data[48:52], 2)
        self.vibration = process_fft(data[52:])

def process_data(data, repo):
    status = HiveStatus(data)

    repo.store_simple("boxlid", status.openness)
    repo.store_simple("light", status.light)
    repo.store_simple("rain", status.rain)
    repo.store_simple("inside_temperature", status.inside_temp)
    repo.store_simple("humidity", status.inside_humidity)
    repo.store_simple("outside_temperature", status.outside_temp)
    repo.store_simple("airpressure", status.outside_pressure)
    repo.store_simple("height", status.altitude)
    repo.store_simple("lpg", status.lpg)
    repo.store_simple("co", status.co)
    repo.store_simple("smoke", status.smoke)
    repo.store_simple("weight", status.weight)
    for frequency, amplitude in status.vibration:
        log.info(frequency, amplitude)
        repo.store_vibration(frequency, amplitude)
    repo.store_simple("dominant_frequency", status.dominant_frequency)
    repo.commit()



def process_fft(data):
    freqs = [0.0, 7.8125, 15.625, 23.4375, 31.25, 39.0625, 46.875, 54.6875, 62.5, 70.3125, 78.125, 85.9375, 93.75, 101.5625, 109.375, 117.1875, 125.0, 132.8125, 140.625, 148.4375, 156.25, 164.0625, 171.875, 179.6875, 187.5, 195.3125, 203.125, 210.9375, 218.75, 226.5625, 234.375, 242.1875, 250.0, 257.8125, 265.625, 273.4375, 281.25, 289.0625, 296.875, 304.6875, 312.5, 320.3125, 328.125, 335.9375, 343.75, 351.5625, 359.375, 367.1875, 375.0, 382.8125, 390.625, 398.4375, 406.25, 414.0625, 421.875, 429.6875, 437.5, 445.3125, 453.125, 460.9375, 468.75, 476.5625, 484.375, 492.1875, 500.0, 507.8125, 515.625, 523.4375, 531.25, 539.0625, 546.875, 554.6875, 562.5, 570.3125, 578.125, 585.9375, 593.75, 601.5625, 609.375, 617.1875, 625.0, 632.8125, 640.625, 648.4375, 656.25, 664.0625, 671.875, 679.6875, 687.5, 695.3125, 703.125, 710.9375, 718.75, 726.5625, 734.375, 742.1875, 750.0, 757.8125, 765.625, 773.4375, 781.25, 789.0625, 796.875, 804.6875, 812.5, 820.3125, 828.125, 835.9375, 843.75, 851.5625, 859.375, 867.1875, 875.0, 882.8125, 890.625, 898.4375, 906.25, 914.0625, 921.875, 929.6875, 937.5, 945.3125, 953.125, 960.9375, 968.75, 976.5625, 984.375, 992.1875]
    ampls = []
    for i in range(0, len(data), 4):
        ampl = get_float(data[i:i+4])
        ampls.append(ampl)
    return tuple(zip(freqs, ampls))

FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT_CONS)


if __name__ == "__main__":
    repo = repo.Repo()
    for data in udp_server():
        log.debug("%r" % (data,))
        process_data(data, repo)
    repo.close()

