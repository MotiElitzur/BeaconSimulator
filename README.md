# Beacon Simulator

A powerful and flexible Bluetooth Low Energy (BLE) beacon simulator designed to run on Raspberry Pi. This project allows you to programmatically control and simulate BLE beacons with customizable MAC addresses, advertisement intervals, and timing sequences.

## 🌟 Features

- **Dynamic MAC Address Control**: Ability to change beacon MAC addresses on the fly
- **Flexible Advertisement Intervals**: Customizable beacon advertisement timing
- **RESTful API Interface**: HTTP endpoints for remote control and monitoring
- **Persistent Storage**: SQLite database for command history and logging
- **Robust Logging System**: Comprehensive logging with database integration
- **Auto-start on Boot**: Automatic service initialization on Raspberry Pi startup

## 🛠️ Prerequisites

- Raspberry Pi (with Bluetooth capability)
- Python 3.x
- Bluetooth and Bluez packages
- Network connectivity

## 📦 Installation

1. Clone the repository:
```bash
git clone [repository-url] BeaconSimulator
cd BeaconSimulator
```

2. Run the setup script:
```bash
./setup_pi.sh
```
The setup script will:
- Install required system packages
- Set up Python virtual environment
- Install Python dependencies
- Configure autostart on boot
- Set up necessary permissions

## 🚀 Usage

### API Endpoints

#### Set Beacon Commands
```http
POST /set_data
Content-Type: application/json

{
    "commands": [
        {
            "type": "mac_change",
            "mac_address": "00:11:22:33:44:55",
            "duration": 30,
            "interval": 800
        },
        {
            "type": "break",
            "duration": 10
        }
    ],
    "is_repetitive": true
}
```

#### Get Current Status
```http
GET /get_data
```

#### Other Available Endpoints
- `GET /ping` - Check server status
- `GET /logs` - Retrieve system logs
- `POST /clear_logs` - Clear log history
- `POST /stop` - Stop beacon simulation
- `POST /reboot` - Reboot the Raspberry Pi

### System Architecture

The project consists of several key components:

- **BeaconManager**: Core class managing BLE beacon operations
- **HttpServer**: Flask-based REST API server
- **Logger**: Singleton logger with database integration

## 📝 Logging

The system maintains logs in two formats:
1. File-based logs (`BeaconSimulator.log`)
2. SQLite database entries (accessible via API)

## ⚙️ Configuration

The server runs on port 2345 by default. Configuration can be modified in the following files:
- `HttpServer.py` - Server settings
- `BeaconManager.py` - Beacon configuration
- `Logger.py` - Logging preferences

## 🔒 Security Notes

- Ensure proper network security as the service runs with sudo privileges
- Consider implementing authentication for production environments
- Review and adjust file permissions as needed

## 🐛 Troubleshooting

1. If the beacon is not advertising:
   - Check Bluetooth service status
   - Verify hci0 interface is up
   - Review system logs

2. If the server is not responding:
   - Check if the service is running
   - Verify network connectivity
   - Review startup logs

## 📜 License

[License Type] - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
