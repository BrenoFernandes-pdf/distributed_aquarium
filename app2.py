import socket
import generated.messages_pb2 as messages_pb2

def main():
    address = ("127.0.0.1", 37021)

    try:
        stream = socket.create_connection(address)
        print(f"Connected to the gateway at {address[0]}:{address[1]}")
    except Exception as e:
        print(f"Failed to connect to the gateway: {e}")
        return

    while True:
        user_input = input("Enter a command (list, get <args>, set <args>) or type 'exit' to quit: ").strip()
        
        if user_input.lower() == "exit":
            print("Exiting application.")
            break

        if not user_input:
            print("Empty input. Please enter a valid command.")
            continue

        parts = user_input.split(" ", 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if command not in ["list", "get", "set"]:
            print("Invalid command. Please use 'list', 'get', or 'set'.")
            continue

        # Serialize the AppMessage
        request = messages_pb2.AppMessage(command=command, args=args)
        serialized_request = request.SerializeToString()

        try:
            # Send only the serialized Protobuf data (no size prefix)
            stream.sendall(serialized_request)
            print("Request sent successfully.")
        except Exception as e:
            print(f"Failed to send request: {e}")
            continue

        try:
            # Receive response from the server
            response_data = stream.recv(1024)
            if not response_data:
                print("Server sent empty response.")
                continue

            # Deserialize the GatewayMessage
            response = messages_pb2.GatewayMessage()
            response.ParseFromString(response_data)

            print(f"Received response type: {response.response_type}")
            if not response.device:
                print("No devices found in the response.")

            for device in response.device:
                print("--- Device Information ---")
                print(f"Address: {device.address}")
                print(f"Type: {device.type}")
                print(f"Status: {device.status}")
                print(f"Value: {device.temp}°C")
                print("---------------------------")

        except Exception as e:
            print(f"Failed to decode or process response: {e}")

    stream.close()
    print("Disconnected.")

if __name__ == "__main__":
    main()

