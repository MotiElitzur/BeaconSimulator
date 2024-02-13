from flask import Flask, request, jsonify
import sqlite3
import json
import os
from BeaconManager import BeaconManager
from Logger import Logger

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
    conn.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY,
                        events TEXT,
                        is_repetitive INTEGER DEFAULT 0,
                        timestamp TEXT)''')
    
    conn.commit()
    conn.close()
    Logger().info("HttpServer initialized")


def load_and_process_latest_events():
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM events ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    if entry:
        events_data = json.loads(entry['events'])
        is_repetitive = bool(entry['is_repetitive'])  # Convert integer to boolean
        manager.update_events(events_data, is_repetitive)
    else:
        Logger().debug("load_and_process_latest_events No events found in the database.")


@flask.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    events = json.dumps(data['events'])
    timestamp = data['timestamp']
    is_repetitive = int(data.get('is_repetitive', False))  # Convert boolean to integer

    conn = get_db_connection()
    conn.execute('INSERT INTO events (events, is_repetitive, timestamp) VALUES (?, ?, ?)',
                 (events, is_repetitive, timestamp))
    conn.commit()
    conn.close()

    # Convert is_repetitive back to boolean before passing to update_events
    manager.update_events(json.loads(events), is_repetitive=bool(is_repetitive))

    return jsonify({"status": "success", "message": "Command received and saved"}), 200

@flask.route('/get_data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM events ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()    
    
    if entry:
        data = {
            "events": json.loads(entry['events']),
            "timestamp": entry['timestamp']
        }
    else:
        data = {"message": "No data found"}
    
    return jsonify({"status": "success", "data": data}), 200

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
    
    return jsonify({"status": "success", "logs": [dict(log) for log in logs]}), 200

if __name__ == '__main__':
    init_db()  # Initialize the database
    load_and_process_latest_events()

    flask.run(host='0.0.0.0', port=2345)