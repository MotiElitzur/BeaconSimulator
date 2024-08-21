#!/bin/bash

# Function to determine the Raspberry Pi IP
# Please note that sometimes the Raspberry Pi name ends with .local (e.g., moti.local), 
# while other times it does not (e.g., moti). This applies to Postman commands as well."
get_raspberry_pi_ip() {

    # local ip="192.168.128.36"
    # echo "$ip"


    local ip="$RASPBERRY_PI_USER.local"
    # Try to ping the .local address
    if dscacheutil -q host -a name "$ip" &> /dev/null; then
        echo "$ip"
    else
        echo "$RASPBERRY_PI_USER" # Use the fallback IP or other method
    fi
}

# Variables
# Ask the user for Raspberry Pi username
echo "Please enter the Raspberry Pi username:"
read RASPBERRY_PI_USER

# Get the Raspberry Pi IP using the function
RASPBERRY_PI_IP=$(get_raspberry_pi_ip)

FOLDER_NAME='BeaconSimulator'
PYTHON_FOLDER_NAME='src'

TARGET_PATH_ON_PI="/home/$RASPBERRY_PI_USER/"
PATH_TO_FOLDER="$TARGET_PATH_ON_PI$FOLDER_NAME"
PATH_TO_PYTHON_SCRIPT="$PATH_TO_FOLDER/$PYTHON_FOLDER_NAME/HttpServer.py"

echo "The Raspberry Pi full ssh adress is $RASPBERRY_PI_USER@$RASPBERRY_PI_IP"

# Make the Python script executable for local use
chmod -R +x "."

# Delete the target directory on the Raspberry Pi
sshpass -p "$RASPBERRY_PI_USER" ssh "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP" "rm -rf $TARGET_PATH_ON_PI/$FOLDER_NAME"

# Copy the entire BeaconSimulator (current) folder to Raspberry Pi, excluding hidden files and the venv folder
sshpass -p "$RASPBERRY_PI_USER" rsync -avz --delete \
--exclude '.*' \
--exclude 'venv/' \
--exclude '*.db' \
--exclude '*.log' \
"../$FOLDER_NAME" "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP:$TARGET_PATH_ON_PI"

# SSH and set up script to run at boot using crontab
sshpass -p "$RASPBERRY_PI_USER" ssh -o StrictHostKeyChecking=no "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP" <<EOF

# Update the raspberry pi, and remove unnecessary packages if any
sudo apt update && sudo apt upgrade && sudo apt autoremove

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y bluetooth bluez

# Navigate to the project directory
cd "$PATH_TO_FOLDER"

# Make the all files executable
chmod -R +x "./"

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip itself
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

#clear the old cron jobs
crontab -r

# Add a cron job to run the Python script at reboot
echo "@reboot python3 $PATH_TO_PYTHON_SCRIPT >> $PATH_TO_FOLDER/startup.log 2>&1" | crontab -

# List the cron jobs
crontab -l

EOF

RASPBERRY_PI_IP=$(get_raspberry_pi_ip)  # Re-evaluate the IP to ensure it's up-to-date
sshpass -p "$RASPBERRY_PI_USER" ssh "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP" "sudo reboot"

echo "The Setup is complete. The Raspberry Pi will reboot now. Please wait for the Raspberry Pi to come back online and then run the http commands" 