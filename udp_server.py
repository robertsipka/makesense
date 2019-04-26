import logging
import socket
import struct

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

def process_sensors(data):
#    for i in range(0,len(data), 4):
#        print("%r" % data[i:i+4])
    print(get_float(data[0:4])) # open/close
    print(get_float(data[4:8])) # gas sensor LPG
    print(get_float(data[8:12])) # gas sensor CO
    print(get_float(data[12:16])) # gas sensor SMOKE
    print(get_float(data[16:20], 2)) # bmp temp
    print(get_float(data[20:24], 2)) # bmp pressure
    print(get_float(data[24:28])) # bmp altitude
    print(get_float(data[28:32], 2)) # sht temp
    print(get_float(data[32:36], 2)) # sht humidity
    print(get_float(data[36:40])) # rain sensor
    print(get_float(data[40:44], 2)) # hx711 weight
    print(get_float(data[44:48])) # lightsensor
    print(get_float(data[48:52], 2)) # FFT dom.

FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

for data in udp_server():
    log.debug("%r" % (data,))
    if data[0] == 0x01:
        size = len(data)
        process_sensors(data[1:size])

