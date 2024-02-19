#!/bin/bash

# Variables
# Ask the user for Raspberry Pi username
echo "Please enter the Raspberry Pi username:"
read RASPBERRY_PI_USER

# RASPBERRY_PI_USER='moti' # Make sure to use straight quotes here
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

# Configure the Bluetooth adapter to be discoverable
# sudo hciconfig hci0 up
#sudo hciconfig hci0 leadv 3

# Navigate to the project directory
cd "$PATH_TO_FOLDER"

# Make the all files executable
chmod -R +x "./"

# Terminate any currently running instances of the Python script
#killall -9 $PYTHON_SCRIPT_NAME

# rm -f $PATH_TO_FOLDER/database.db

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip itself
pip install --upgrade pip

# Install dependencies from requirements.txt              TODO: Uncomment this line if its already installed because it will take a long time to install
pip install -r requirements.txt

#clear the old cron jobs
crontab -r

# Add a cron job to run the Python script at reboot
echo "@reboot python3 $PATH_TO_PYTHON_SCRIPT >> $PATH_TO_FOLDER/$FOLDER_NAME.log 2>&1" | crontab -

# List the cron jobs
crontab -l

# Run the Python script immediately and redirect output to the log file
# nohup python3 $PATH_TO_PYTHON_SCRIPT >> $PATH_TO_FOLDER/$FOLDER_NAME.log 2>&1 &

EOF