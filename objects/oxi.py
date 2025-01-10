import socket
import threading
import time

from client import Client
class Ox(Client):

    def __init__(self, state, oxi):
        self.state = True
        self.oxi = 9
        self.type = 'Oxigenio'

    def connect_tcp(self, addr):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(addr)
        client_socket.connect(addr)
        print("Connected to Gateway!")

        receive_thread = threading.Thread(target = self.receive, args=(client_socket,))
        receive_thread.start()

        update_thread = threading.Thread(target=self.periodic_update, args=(client_socket,))
        update_thread.start()

        return client_socket
    
    def receive(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode(Client.FORMAT)
                print(f"Received Command: {message}")

                if message.split()[0] == "set_status":
                    if message.split()[1] == "true":
                        self.state = True
                    elif message.split()[1] == "false":
                        self.state = False
                    else:
                        pass
                    print(f"New status:{self.state}")

                elif message.split()[0] == "set_oxi":
                    self.oxi = int(message.split()[1])
                    print(f"New oxygen rate:{self.oxi}")
                else:
                    pass
            except:
                print("An error occured!")
                client_socket.close()
                break

    def periodic_update(self, client_socket):
        while True:
            time.sleep(5)
            msg = f"info {self.oxi} {self.state}"
            self.write(client_socket, msg)

