import socket
import json
import struct


def get_command_input(request):
    command = input("Please enter the wanted command: ")
    request["command"] = command
    return request


def print_command_output(response):
    print(f"Received response:\n {response.decode('utf-8')}")


def get_screenshot_input(request):
    return request


def handle_screenshot(data):
    with open('received_screenshot.png', 'wb') as f:
        f.write(data)


actions = {
    "command": {
        "input": get_command_input,
        "output": print_command_output
    },
    "screenshot": {
        "input": get_screenshot_input,
        "output": handle_screenshot
    }
}


def get_user_input():
    request = {
    }
    action = input("Please enter the wanted action (command): ")
    request["type"] = action
    if action in actions:
        actions[action]["input"](request)

    return request


def receive_all(client_socket, size):
    data = b''
    while len(data) < size:
        data += client_socket.recv(size - len(data))
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
            client_socket.send(json.dumps(request).encode('utf-8'))
            print(f"Sent command: {request}")
            size = struct.unpack(">I", client_socket.recv(4))[0]
            # Receive response from client
            response = receive_all(client_socket, size)
            if request["type"] in actions:
                actions[request["type"]]["output"](response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()
        print("Sockets closed.")


if __name__ == "__main__":
    main()
