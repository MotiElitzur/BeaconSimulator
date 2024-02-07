import os
import subprocess

# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the http_server.py script
script_path = os.path.join(script_dir, "http_server.py")

def start_up():
    try:
        # Specify the Python interpreter explicitly
        subprocess.run(['python3', script_path], check=True)
        print("Server started")
    except subprocess.CalledProcessError as e:
        print(f"Server start Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

start_up()