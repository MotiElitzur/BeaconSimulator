from flask import Flask, request, jsonify
import sqlite3
import json
import os
from BeaconManager import BeaconManager
from Logger import Logger
from datetime import datetime

flask = Flask(__name__)

# Set the database file to be in the same directory as the script
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

manager = BeaconManager()

def init_db():
    conn = get_db_connection()                 
    conn.execute('''CREATE TABLE IF NOT EXISTS commands (
                        id INTEGER PRIMARY KEY,
                        commands TEXT,
                        is_repetitive INTEGER DEFAULT 0,
                        timestamp TEXT)''')
    
    conn.commit()
    conn.close()
    Logger().info("HttpServer initialized")


def load_and_process_latest_commands():
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM commands ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    if entry:
        commands_data = json.loads(entry['commands'])
        is_repetitive = bool(entry['is_repetitive'])  # Convert integer to boolean
        manager.update_commands(commands_data, is_repetitive)
    else:
        Logger().debug("load_and_process_latest_commands No commands found in the database.")


@flask.route('/set_data', methods=['POST'])
def handle_command():
    data = request.json
    commands = json.dumps(data['commands'])
    timestamp = data['timestamp']
    is_repetitive = int(data.get('is_repetitive', False))  # Convert boolean to integer

    conn = get_db_connection()
    conn.execute('INSERT INTO commands (commands, is_repetitive, timestamp) VALUES (?, ?, ?)',
                 (commands, is_repetitive, timestamp))
    conn.commit()
    conn.close()

    # Convert is_repetitive back to boolean before passing to update_commands
    manager.update_commands(json.loads(commands), is_repetitive=bool(is_repetitive))

    return jsonify({"status": "success", "message": "Set data received and saved"}), 200

@flask.route('/get_data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM commands ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()    
    
    if entry:
        data = {
            "commands": json.loads(entry['commands']),
            "timestamp": entry['timestamp']
        }
    else:
        data = {"message": "No data found"}
    
    return jsonify({"status": "success", "data": data}), 200

@flask.route('/stop', methods=['POST'])
def stop():
    manager.stop()
    return jsonify({"status": "success", "message": "BeaconManager stopped"}), 200

def start():
    manager.start()
    return jsonify({"status": "success", "message": "BeaconManager started"}), 200

@flask.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success", "message": "Server is alive"}), 200

@flask.route('/logs', methods=['GET'])
def get_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs')
    logs = cursor.fetchall()
    conn.close()
    
    formatted_logs = [f"{log['id']}-{log['timestamp']}-{log['level']}-{log['message']}" for log in logs]
    currTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"status": f"success current time {currTime}", "logs": formatted_logs}), 200

if __name__ == '__main__':
    init_db()  # Initialize the database
    load_and_process_latest_commands()
    
    flask.run(host='0.0.0.0', port=2345)