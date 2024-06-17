#!/bin/bash

# Variables
# Ask the user for Raspberry Pi username
echo "Please enter the Raspberry Pi username:"
read RASPBERRY_PI_USER

RASPBERRY_PI_IP="$RASPBERRY_PI_USER.local"

FOLDER_NAME='BeaconSimulator'
PYTHON_FOLDER_NAME='src'

TARGET_PATH_ON_PI="/home/$RASPBERRY_PI_USER/"
PATH_TO_FOLDER="$TARGET_PATH_ON_PI$FOLDER_NAME"
PATH_TO_PYTHON_SCRIPT="$PATH_TO_FOLDER/$PYTHON_FOLDER_NAME/HttpServer.py"

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

sshpass -p "$RASPBERRY_PI_USER" ssh "$RASPBERRY_PI_USER@$RASPBERRY_PI_IP" "sudo reboot"

echo "The Setup is complete. The Raspberry Pi will reboot now. Please wait for the Raspberry Pi to come back online and then run the http commands" 