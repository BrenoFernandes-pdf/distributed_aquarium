import socket
import threading

from multicast.receive_multicast_group import receive_multicast

class Client:
    FORMAT = "utf-8"
    
    def get_addr_by_mult(self):
        addr = receive_multicast().decode(Client.FORMAT)
        # Tratando o fortmato da mensagem
        print(f"Mensagem recebida pelo multicast: {addr}")  # Adicionado para debug
        addr = addr.split()
        addr[1] = int(addr[1])
        addr = tuple(addr)

        return addr

    def receive(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode(Client.FORMAT)
                print(message)
            except:
                print("An error occured!")
                client_socket.close()
                break

    def write(self, client_socket, msg):
        client_socket.send(msg.encode(Client.FORMAT))

    def connect_tcp(self, addr):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(addr)
        client_socket.connect(addr)
        print("Connected to Gateway!")

        receive_thread = threading.Thread(target = self.receive, args=(client_socket,))
        receive_thread.start()

        return client_socket