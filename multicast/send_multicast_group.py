import socket
import struct
import sys

def send_multicast(message):
    multicast_group = ('224.3.29.71', 10000)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.settimeout(0.2)

    # Seta o time-to-live da mensagem para 1 
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        print('Sending by multicast "%s"\n' %message)
        message = message.encode('UTF-8')
        sock.sendto(message, multicast_group)

    finally:
        print('Closing multicast socket\n')
        sock.close()