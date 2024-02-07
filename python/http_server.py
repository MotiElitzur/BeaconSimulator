from flask import Flask, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)
# Set the database file to be in the same directory as the script
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS database (
                        id INTEGER PRIMARY KEY,
                        mac_addresses TEXT,
                        interval_time INTEGER,
                        timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    mac_addresses = json.dumps(data['mac_addresses'])
    interval_time = data['interval_time']
    timestamp = data['timestamp']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO database (mac_addresses, interval_time, timestamp) VALUES (?, ?, ?)',
                 (mac_addresses, interval_time, timestamp))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Command received and saved"}), 200

@app.route('/get_data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM database ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    
    if entry:
        data = {
            "mac_addresses": json.loads(entry['mac_addresses']),
            "interval_time": entry['interval_time'],
            "timestamp": entry['timestamp']
        }
    else:
        data = {"message": "No data found"}
    
    return jsonify({"status": "success", "data": data}), 200

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success", "message": "Server is alive"}), 200

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(host='0.0.0.0', port=2345)


# @app.route('/command', methods=['POST'])
# def handle_command():
#     # Extract data from the request
#     data = request.json
#     print(f"Received command: {data}")
    
#     # Perform actions based on the received command
#     # Placeholder for command handling logic

#     # Respond to the sender
#     return jsonify({"status": "success", "message": f"Command received {data}"}), 200


# @app.route('/ping', methods=['GET'])
# def ping():
#     return jsonify({"status": "success", "message": "Server is alive"}), 200


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=2345)