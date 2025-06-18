import socket


def get_user_input():
    request = {
    }
    action = input("Please enter the wanted action (command): ")
    request["type"] = action
    if action == "command":
        command = input("Pleae enter the wanted command: ")
        request["command"] = command
    return request

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
            command = get_user_input()
            if not command:
                print("No valid command provided. Closing connection.")
                break
            client_socket.send(command.encode('utf-8'))
            print(f"Sent command: {command}")

            # Receive response from client
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                print("No response received or client disconnected.")
                break
            print(f"Received response: {response}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        server_socket.close()
        print("Sockets closed.")

if __name__ == "__main__":
    main()