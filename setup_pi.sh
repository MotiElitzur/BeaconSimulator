#!/bin/bash

# Variables
RASPBERRY_PI_USER='moti' # Make sure to use straight quotes here
RASPBERRY_PI_IP='raspberrypi.local'
BEACON_SIMULATOR_FOLDER_NAME='BeaconSimulator'
TARGET_PATH_ON_PI="/home/$RASPBERRY_PI_USER/"
SSH_PASSWORD='moti'  # Be very cautious with storing passwords like this
PYTHON_FOLDER_NAME='src'

# Make the Python script executable for local use
chmod -R +x "."

# Copy the entire BeaconSimulator (current) folder to Raspberry Pi
sshpass -p "$SSH_PASSWORD" rsync -avz --delete --exclude '.*' --exclude "venv/" "../$BEACON_SIMULATOR_FOLDER_NAME" "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP:$TARGET_PATH_ON_PI"

# SSH and set up script to run at boot using crontab
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP" <<EOF

# Navigate to the project directory
cd "$TARGET_PATH_ON_PI$BEACON_SIMULATOR_FOLDER_NAME"

# Make the all files executable
chmod -R +x "./"

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt              TODO: Uncomment this line if its already installed because it will take a long time to install
pip install -r requirements.txt

#clear the old cron jobs
crontab -r

# Add a cron job to run the Python script at reboot
echo "@reboot python3 $TARGET_PATH_ON_PI$BEACON_SIMULATOR_FOLDER_NAME/$PYTHON_FOLDER_NAME/HttpServer.py >> $TARGET_PATH_ON_PI$BEACON_SIMULATOR_FOLDER_NAME/startup.log 2>&1" | crontab -

# List the cron jobs
crontab -l

EOF