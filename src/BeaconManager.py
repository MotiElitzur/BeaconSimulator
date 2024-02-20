import time
from threading import Thread, Event
from Logger import Logger
import subprocess

class BeaconManager:

    logger = Logger()

    def __init__(self, is_repetitive=False):
        self._commands = None
        self.is_repetitive = is_repetitive
        self.current_mac_address = None

        self.commands_updated = Event()

        self._thread = Thread(target=self.run, args=())
        self._thread.daemon = True  # Daemonize thread
        self._thread.start()

    def run(self):

        while True:
            Logger().info("BeaconManager start waiting for commands...")
            self.commands_updated.wait()  # Wait until commands are updated
            self.commands_updated.clear()  # Reset the command flag after receiving commands.

            Logger().info("BeaconManager received new commands")

            while True:  # Outer loop for handling repetition

                if self._commands is None:  # Check if there are commands to process
                    Logger().info("No commands to process, waiting for new commands...")
                    subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                    break  # Exit the loop if no commands are set, and return to waiting state.

                for command in self._commands:
                    duration = command.get('duration', 0)  # Using a consistent name for duration

                    if command.get('type') == 'mac_change':
                        self.current_mac_address = command['mac_address']
                        beacon_mac_as_bytes = self.current_mac_address.replace(":", " ")
                        command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "  # Adjusted to include a more generic company identifier
                        command_end = " BB BB BB"
                        full_command = command_start + beacon_mac_as_bytes + command_end

                        # Execute the full command
                        try:
                            subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                            subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)  # Ensure Bluetooth is on
                            subprocess.run('sudo hciconfig hci0 leadv 3', shell=True, check=True)

                            result = subprocess.run(full_command, shell=True, check=True, stderr=subprocess.PIPE)
                            Logger().info(f"Changing mac to {self.current_mac_address} for {duration} seconds")
                            # Logger().info(f"Changing mac executed successfully. {result}")
                        except subprocess.CalledProcessError as e:
                            Logger().error(f"Failed to execute change mac command: {e}")


                    elif command.get('type') == 'break':
                        # Turning Bluetooth off
                        Logger().info(f"Breaking command. Turning off Bluetooth for {duration} seconds...")
                        subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                        self.current_mac_address = "BREAK"


                        # # Turning Bluetooth back on
                        # subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)
                        # subprocess.run('sudo hciconfig hci0 leadv 3', shell=True, check=True)

                    else:
                        Logger().error(f"Unknown command type {command.get('type')}")
                        # self.commands_updated.wait(duration)


                    if self.commands_updated.wait(timeout=duration):
                        self.commands_updated.clear()
                        self.logger.info("New commands received, stopping current operation., during sleep time.")
                        break  # Exit current comman


    def update_commands(self, new_commands, is_repetitive=True):
        # Update the commands and the is_repetitive flag here
        Logger().info(f"BeaconManager updating commands, new commands size: {len(new_commands)}, is_repetitive: {is_repetitive}")

        self._commands = new_commands
        self.is_repetitive = is_repetitive  # Update the repetitive flag based on new input
        self.commands_updated.set()  # Notify the run method that commands have been updated

    def stop(self):
        Logger().info("BeaconManager stopp called")
        self._commands = None
        self.commands_updated.set()
