from client import Client
import generated.messages_pb2 as message_pb2
class Lamp(Client):

    def __init__(self, state):
        self.state = False
        self.type = 'luz_branca'

    def receive(self, client_socket):
        while True:
            try:
                raw_message = client_socket.recv(1024)
                command = message_pb2.DeviceMessage()
                command.ParseFromString(raw_message)
                message = command.data
                print(f"Received command: {message}") 

                if message.split()[0] == "set_status":
                    if message.split()[1] == "true":
                        self.state = True
                    elif message.split()[1] == "false":
                        self.state = False
                    else:
                        pass
                    print(f"New status:{self.state}")

                elif message.split()[0] == "get_status":
                    msg = f"info {self.state}"
                    self.write(client_socket, msg)
                else:
                    pass
            except:
                print("An error occured!")
                client_socket.close()
                break