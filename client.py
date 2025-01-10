import socket
import threading
import generated.messages_pb2 as messages_pb2
from multicast.receive_multicast_group import receive_multicast

class Client:
    FORMAT = "utf-8"

    def get_addr_by_mult(self):
        addr = receive_multicast().decode(Client.FORMAT)
        # Tratando o formato da mensagem
        print(f"Mensagem recebida pelo multicast: {addr}")  # Adicionado para debug
        addr = addr.split()
        addr[1] = int(addr[1])
        addr = tuple(addr)

        return addr

    def receive(self, client_socket):
        while True:
            try:
                raw_message = client_socket.recv(1024)
                message = messages_pb2.DeviceMessage()
                message.ParseFromString(raw_message)
                print(message.data)
            except:
                print("An error occured!")
                client_socket.close()
                break

    def write(self, client_socket, msg):
        message = messages_pb2.DeviceMessage(data=msg)
        serialized_message = message.SerializeToString()
        client_socket.send(serialized_message)

    def connect_tcp(self, addr):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(addr)
        client_socket.connect(addr)
        print("Connected to Gateway!")
        

        receive_thread = threading.Thread(target = self.receive, args=(client_socket,))
        receive_thread.start()

        return client_socket