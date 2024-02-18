import time
from threading import Thread, Event
from Logger import Logger
import subprocess

class BeaconManager:

    def __init__(self, is_repetitive=False):

        # initialize data
        self._commands = None
        self.is_repetitive = is_repetitive

        # Create events for synchronization
        self.commands_updated = Event()
        self.be_ready_for_new_commands = Event()

        # Start the thread
        self._thread = Thread(target=self.run, args=())
        self._thread.daemon = True  # Ensure thread closes with the program
        self._thread.start()

    def run(self):

        while True:
            Logger().info("BeaconManager start waiting for commands...")
            self.commands_updated.wait()  # Wait until commands are updated
            self.commands_updated.clear()  # Reset the command flag after receiving commands

            Logger().info("BeaconManager received new commands")

            while True:  # Outer loop for handling repetition
                for command in self._commands:
                    duration = command.get('duration', 0)  # Using a consistent name for duration

                    if command.get('type') == 'mac_change':
                        mac_address = command['mac_address']
                        beacon_mac_as_bytes = mac_address.replace(":", " ")
                        command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "  # Adjusted to include a more generic company identifier
                        command_end = " BB BB BB"
                        full_command = command_start + beacon_mac_as_bytes + command_end

                        # Execute the full command
                        try:
                            Logger().info(f"Changing mac to {mac_address}")

                            # Reset Bluetooth connection, this is necessary to avoid issues with the Bluetooth adapter
                            subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                            subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)  # Ensure Bluetooth is on
                            subprocess.run('sudo hciconfig hci0 leadv 3', shell=True, check=True)

                            result = subprocess.run(full_command, shell=True, check=True, stderr=subprocess.PIPE)
                            # Logger().info(f"Changing mac executed successfully. {result}")
                        except subprocess.CalledProcessError as e:
                            Logger().error(f"Failed to execute command: {e}\nSTDERR: {e.stderr.decode()}")

                        Logger().info(f"Changing mac to {mac_address} and waiting for {duration} seconds")

                    elif command.get('type') == 'break':
                        # Turning Bluetooth off
                        Logger().info(f"Breaking command. Turning off Bluetooth for {duration} seconds...")
                        subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                        # # Turning Bluetooth back on
                        # subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)
                        # subprocess.run('sudo hciconfig hci0 leadv 3', shell=True, check=True)

                    else:
                        Logger().error(f"Unknown command type {command.get('type')}")

                    # Sleep for the duration of the command, unless new commands are received
                    if self.be_ready_for_new_commands.wait(timeout=duration):
                        self.be_ready_for_new_commands.clear()
                        self.logger.info("New commands received, stopping current operation., during sleep time.")
                        break  # Exit current while loop if new commands are received

                    # Check if new commands were received during execution
                    if self.ready_for_new_commands.is_set():
                        Logger().info("New commands received, stopping current operation.")
                        break  # Break from command processing loop to handle new commands
        
                if not self.is_repetitive:
                    Logger().info(f"Current commands not repetitive and comes to end, breaking the loop.")
                    break

                if self.be_ready_for_new_commands.is_set():
                    Logger().info(f"BeaconManager received new commands, breaking the loop.")
                    break

    def update_commands(self, new_commands, is_repetitive=False):
        # Update the commands and the is_repetitive flag here
        Logger().info(f"BeaconManager updating commands, new commands size: {len(new_commands)}, is_repetitive: {is_repetitive}")
        self.be_ready_for_new_commands.set()  # Notify the run method that new commands are ready

        self._commands = new_commands
        self.is_repetitive = is_repetitive  # Update the repetitive flag based on new input
        self.commands_updated.set()  # Notify the run method that commands have been updated