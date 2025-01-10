import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import generated.messages_pb2 as pb
from multicast.send_multicast_group import send_multicast

IP = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"

class IoTGateway:
    def __init__(self, tcp_port_devices=37020, tcp_port_app=37021, udp_port=8081, multicast_group="224.0.0.1"):
        self.tcp_port_devices = tcp_port_devices
        self.tcp_port_app = tcp_port_app
        self.udp_port = udp_port
        self.multicast_group = multicast_group
        self.devices = {}
        
        self.lock = threading.Lock()

    def start(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.executor.submit(self.tcp_server_devices)
        self.executor.submit(self.tcp_server_app)
        self.executor.submit(self.udp_server)
        self.executor.submit(self.multicast_discovery)
        self.send_gateway_address()

    def tcp_server_devices(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("", self.tcp_port_devices))
            server.listen()
            print(f"TCP server for devices listening on port {self.tcp_port_devices}")

            while True:
                client, addr = server.accept()
                print(f"New TCP connection from device {addr}")
                threading.Thread(target=self.handle_device, args=(client, addr)).start()

    def tcp_server_app(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("", self.tcp_port_app))
            server.listen()
            print(f"TCP server for application listening on port {self.tcp_port_app}")

            while True:
                client, addr = server.accept()
                print(f"New TCP connection from application {addr}")
                threading.Thread(target=self.handle_app, args=(client,)).start()

    def udp_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            server.bind(("", self.udp_port))
            print(f"UDP server listening on port {self.udp_port}")

            while True:
                data, addr = server.recvfrom(1024)
                print(f"Received UDP message from {addr}")
                message = pb.Object()
                message.ParseFromString(data)
                self.register_device(message, addr)

    def multicast_discovery(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", self.udp_port))

            mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton("0.0.0.0")
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            while True:
                data, addr = sock.recvfrom(1024)
                print(f"Received multicast message from {addr}")
                message = pb.Object()
                message.ParseFromString(data)
                self.register_device(message, addr)

    def send_gateway_address(self):
        message = f"{IP} {self.tcp_port_devices}"
        print(f"Sending gateway address to multicast group: {message}")
        send_multicast(message)

    def handle_device(self, client, addr):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    print(f"Device {addr} disconnected.")
                    break

                message = pb.DeviceMessage()
                message.ParseFromString(data)

                print(f"Received from device {addr}: {message.data}")
                if message.data.split()[0] == "info":
                    self.update_device_state(addr, message)

            except Exception as e:
                print(f"Error handling device {addr}: {e}")
                client.close()
                break

    def handle_app(self, client):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    print("Application client disconnected.")
                    break

                app_message = pb.AppMessage()
                app_message.ParseFromString(data)

                command = app_message.command
                args = app_message.args

                print(f"Received command: {command} {args}")

                if command == "list":
                    self.handle_list_command(client)
                elif command == "get":
                    self.handle_get_command(client, args)
                elif command == "set":
                    field, device_type, value = args.split(" ", 2)
                    self.handle_set_command(client, field, device_type, value)
                else:
                    response = f"Unknown command: {command}\n"
                    client.send(response.encode(FORMAT))

            except Exception as e:
                print(f"Error handling application client: {e}")
                client.close()
                break

    def handle_list_command(self, client):
        response = pb.GatewayMessage(response_type=pb.GatewayMessage.LIST)
        with self.lock:
            for addr, device in self.devices.items():
                obj = pb.Object(
                    address=device["address"],
                    type=device["type"],
                    status=device["status"],
                    temp=device["value"]
                )
                response.device.append(obj)

        client.send(response.SerializeToString())

    def handle_get_command(self, client, args):
        response = pb.GatewayMessage(response_type=pb.GatewayMessage.GET)
        with self.lock:
            # Busca o dispositivo pelo campo `type`
            for addr, device in self.devices.items():
                if device["type"] == args.split()[1]:
                    obj = pb.Object(
                    address=device["address"],
                    type=device["type"],
                    status=device["status"],
                    temp=device["value"]
                )
                response.device.append(obj)
                break  # Para no primeiro dispositivo encontrado com o tipo desejado
        client.send(response.SerializeToString())

    def handle_set_command(self, client, field, device_type, value):
        response = pb.GatewayMessage(response_type=pb.GatewayMessage.UPDATE)
        with self.lock:
            # Busca o dispositivo pelo campo `type`
            device = None
            for addr, dev in self.devices.items():
                if dev["type"] == device_type:
                    device = dev
                    break

            if not device:
                client.send(response.SerializeToString())
                
        # Atualiza o campo especificado
        if(device):
            if field == "status":
                device["status"] = value
            elif field == "value":
                device["value"] = int(value)
            else:
                pass
        
        client.send(response.SerializeToString())

    def register_device(self, message, addr):
        with self.lock:
            self.devices[addr] = {
                "address": addr,
                "type": message.type,
                "status": message.status,
                "value": message.temp,
            }
        print(f"Registered device {message.type} at {addr}")

    def update_device_state(self, addr, message):
        with self.lock:
            if addr in self.devices:
                self.devices[addr]["status"] = message.data
                print(f"Updated state for device {addr}: {message.data}")

if __name__ == "__main__":
    gateway = IoTGateway()
    gateway.start()
