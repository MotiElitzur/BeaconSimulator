# Beacon Simulator Server

A powerful and flexible server application for Bluetooth Low Energy (BLE) beacon simulation, designed to run on Raspberry Pi. This Flask-based server enables programmatic control of Eddystone beacons through a REST API, allowing dynamic management of MAC addresses, advertisement intervals, and timing sequences. The server can be controlled remotely through HTTP requests, making it ideal for automated testing and beacon deployment scenarios.

## 🌟 Features

- **Dynamic MAC Address Control**: Ability to change beacon MAC addresses on the fly
- **Flexible Advertisement Intervals**: Customizable beacon advertisement timing
- **RESTful API Interface**: HTTP endpoints for remote control and monitoring
- **Persistent Storage**: SQLite database for command history and logging
- **Robust Logging System**: Comprehensive logging with database integration
- **Auto-start on Boot**: Automatic service initialization on Raspberry Pi startup
- **Eddystone Protocol Support**: Full support for Eddystone beacon format
- **Flutter UI Integration**: Compatible with Flutter-based control interface

## 🛠️ Prerequisites

### Hardware Requirements
- Raspberry Pi (Zero W, Zero 2 W, or newer)
- Bluetooth capability
- Network connectivity

### Software Requirements
- Raspberry Pi OS (32-bit for Pi Zero)
- Python 3.x
- OpenJDK 8 (for Pi Zero W due to 32-bit limitation)
- Bluetooth and Bluez packages
- VNC Server (optional for remote desktop)

## 📦 Installation

### Setting Up the Raspberry Pi

1. Install Raspberry Pi OS:
   ```bash
   # Use Raspberry Pi Imager to flash the OS
   # Configure WiFi and hostname during installation
   ```

2. Initial System Setup:
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade
   
   # Install required packages
   sudo apt install bluetooth bluez openjdk-8-jdk-headless
   ```

3. Configure VNC (Optional):
   ```bash
   # Run raspi-config
   sudo raspi-config
   # Enable VNC under Interfacing Options
   ```

### Setting Up the Development Environment

1. Install Homebrew (Mac only):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install hudochenkov/sshpass/sshpass
   ```

2. Clone and Deploy:
   ```bash
   git clone [repository-url] BeaconSimulator
   cd BeaconSimulator
   chmod +x setup_pi.sh
   ./setup_pi.sh
   ```

## 🚀 Usage

### Beacon Configuration

The beacon uses the Eddystone protocol with the following structure:
```
Command Structure:
sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 1E 00 00 00 00 05 [MAC] BB BB BB

Where:
- 1E: Packet length (30 bytes)
- 02 01 04: Flags data
- 03 9A FE: Eddystone UUID
- 16: Service data length
- 20: Frame Type (Eddystone-TLM)
- 00: TLM Version
- 0A DA: Battery voltage
- 1E 00: Temperature (30.0°C)
- 00 00 00 05: Advertisement count
- [MAC]: Your beacon MAC address
- BB BB BB: Ending sequence
```

### API Endpoints

#### Set Beacon Commands
```http
POST /set_data
Content-Type: application/json

{
    "commands": [
        {
            "type": "mac_change",
            "mac_address": "DD:34:02:07:5B:D1",
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

#### Status and Control Endpoints
- `GET /get_data` - Retrieve current command configuration
- `GET /ping` - Check server status and current MAC
- `GET /logs` - Retrieve system logs
- `POST /clear_logs` - Clear log history
- `POST /stop` - Stop beacon simulation
- `POST /reboot` - Reboot the Raspberry Pi

### Flutter Integration

The project includes Flutter integration capabilities:
- Device selection interface
- JSON configuration upload
- Multi-device management
- Automated timing calculations
- Database integration for experiment results

## ⚙️ Advanced Configuration

### Bluetooth Setup
```bash
# Enable LE Advertising mode (Nonconnectable undirected)
sudo hciconfig hci0 leadv 3

# Verify Bluetooth status
sudo hciconfig hci0 status
```

### Server Configuration
- Default port: 2345
- Logging: Both file-based and SQLite database
- Auto-start: Configured via crontab during setup

## 🔒 Security Notes

- The service runs with sudo privileges for Bluetooth access
- Consider implementing authentication for production
- Secure network access to the Raspberry Pi
- Regular system updates recommended

## 🐛 Troubleshooting

1. Connection Issues:
   - Verify hostname resolution (`hostname.local` vs `hostname`)
   - Check network connectivity
   - Verify SSH access

2. Beacon Issues:
   - Check Bluetooth service status
   - Verify hci0 interface
   - Review system logs

3. Common Solutions:
   ```bash
   # Restart Bluetooth service
   sudo service bluetooth restart
   
   # Check logs
   tail -f BeaconSimulator/startup.log
   ```

## 📚 Additional Resources

- [Eddystone Protocol Specification](https://github.com/google/eddystone)
- [Flutter Documentation](https://flutter.dev/docs)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)

## 📜 License

[License Type] - See LICENSE file for details
