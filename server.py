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


ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerSocket.bind(("127.0.0.1", 2000))
ServerSocket.listen()
ClientSocket, _ = ServerSocket.accept()
request = get_user_input()
ClientSocket.send()