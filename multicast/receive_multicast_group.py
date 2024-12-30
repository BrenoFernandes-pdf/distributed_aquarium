import socket
import struct
import sys

def receive_multicast():
    multicast_group = '224.3.29.71'
    server_address = ('', 10000)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Solicita ao sistema operacional para adicionar o socket ao grupo multicast em todas as interfaces
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sock.bind(server_address)

    while True:
        print('\nWaiting to receive message by multicast\n')
        data, address = sock.recvfrom(1024)
        
        print('Received %s bytes from %s\n' % (len(data), address))

        if data != None:
            return data