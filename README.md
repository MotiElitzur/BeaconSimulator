# BeaconSimulator

Please note that sometimes the Raspberry Pi name ends with .local (e.g., moti.local), 
while other times it does not (e.g., moti). This applies to Postman commands as well."


// fixing ssh name not working, run it inside the raaspberipy, this example is for bb, replace with your name
#!/bin/bash

# Function to run commands and display output
run_cmd() {
    echo "Running: $1"
    eval "$1"
    echo "Command completed with exit status: $?"
    echo "---"
}

echo "Starting mDNS fix script at $(date)"

# Remove the IP-based entry from /etc/hosts
run_cmd "sudo sed -i '/^192.168.128.36/d' /etc/hosts"

# Ensure correct localhost entries in /etc/hosts
run_cmd "sudo sed -i '1i127.0.0.1\tlocalhost' /etc/hosts"
run_cmd "sudo sed -i '2i::1\t\tlocalhost ip6-localhost ip6-loopback' /etc/hosts"

# Ensure correct hostname entry in /etc/hosts
run_cmd "sudo sed -i 's/^127.0.1.1.*/127.0.1.1\tbb/' /etc/hosts"

# Add mdns4 to nsswitch.conf if not present
run_cmd "grep -q 'mdns4' /etc/nsswitch.conf || sudo sed -i '/^hosts:/ s/$/ mdns4/' /etc/nsswitch.conf"

# Restart Avahi daemon
run_cmd "sudo systemctl restart avahi-daemon"

# Check hostname
run_cmd "hostname"

# Check /etc/hosts
run_cmd "cat /etc/hosts"

# Check nsswitch.conf
run_cmd "cat /etc/nsswitch.conf | grep hosts"

# Check Avahi status
run_cmd "sudo systemctl status avahi-daemon"

# Test mDNS resolution
run_cmd "avahi-resolve -n bb.local"
run_cmd "getent hosts bb.local"

echo "mDNS fix script completed at $(date)"
echo "Please reboot your Raspberry Pi with 'sudo reboot'"
echo "After reboot, try connecting from your Mac with 'ssh bb@bb.local'"

// fix locale
sudo bash -c '
locale-gen en_US.UTF-8
echo "LANG=en_US.UTF-8\nLC_ALL=en_US.UTF-8" > /etc/default/locale
sed -i "/en_US.UTF-8/s/^# //g" /etc/locale.gen
locale-gen
update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
echo "export LANG=en_US.UTF-8\nexport LC_ALL=en_US.UTF-8" >> /root/.bashrc
echo "export LANG=en_US.UTF-8\nexport LC_ALL=en_US.UTF-8" >> /home/bb/.bashrc
apt-get install --reinstall locales -y
apt-get install language-pack-en -y
'
source ~/.bashrc

echo "=== Locale Settings ==="
locale
echo "\n=== Available Locales ==="
locale -a
echo "\n=== /etc/default/locale contents ==="
cat /etc/default/locale
echo "\n=== Relevant lines from /etc/locale.gen ==="
grep "en_US.UTF-8" /etc/locale.gen
echo "\n=== Relevant lines from ~/.bashrc ==="
tail -n 2 ~/.bashrc
echo "\n=== Locale-related environment variables ==="
env | grep -E "LANG|LC_"
sudo reboot
