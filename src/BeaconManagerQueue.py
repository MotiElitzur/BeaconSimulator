import time
from threading import Thread, Lock
from queue import Queue, Empty
import subprocess
from Logger import Logger

class BeaconManager:

    logger = Logger()

    def __init__(self):
        self.commands_queue = Queue()
        self.original_commands = []  # To store the latest set of commands for repetitive execution
        self.is_repetitive = False
        self.lock = Lock()  # Ensure thread-safe operations when modifying commands

        self._thread = Thread(target=self.run, args=())
        self._thread.start()

    def run(self):
        while True:
            try:
                command = self.commands_queue.get(timeout=1)  # Use a timeout to periodically check for new commands
                Logger().info("BeaconManager processing a new command")


                duration = command.get('duration', 0)  # Using a consistent name for duration

                if command.get('type') == 'mac_change':
                    mac_address = command['mac_address']
                    beacon_mac_as_bytes = mac_address.replace(":", " ")
                    command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "  # Adjusted to include a more generic company identifier
                    command_end = " BB BB BB"
                    full_command = command_start + beacon_mac_as_bytes + command_end

                    # Execute the full command
                    try:
                        Logger().info(f"Executing command: {full_command}")
                        subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)  # Ensure Bluetooth is on
                        subprocess.run('sudo hciconfig hci0 leadv 3', shell=True, check=True)  # Ensure advertising is on
                        result = subprocess.run(full_command, shell=True, check=True, stderr=subprocess.PIPE)
                        Logger().info(f"Changing mac executed successfully. {result}")
                    except subprocess.CalledProcessError as e:
                        Logger().error(f"Failed to execute command: {e}\nSTDERR: {e.stderr.decode()}")

                    Logger().info(f"Changing mac to {mac_address} and waiting for {duration} seconds")
                    time.sleep(duration)

                elif command.get('type') == 'break':
                    # Turning Bluetooth off
                    Logger().info(f"Breaking command. Turning off Bluetooth for {duration} seconds...")
                    subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                    time.sleep(duration)
                    # Turning Bluetooth back on
                    subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)

                else:
                    Logger().error("Unknown command type.")

                self.commands_queue.task_done()  # Signal that the command has been processed
            except Empty:
                # Queue is empty; check if we need to requeue commands for repetitive execution
                if self.is_repetitive:
                    with self.lock:
                        for command in self.original_commands:
                            self.commands_queue.put(command)
                        Logger().info("Repetitive mode: Requeued original commands")


    def update_commands(self, new_commands, is_repetitive=False):
        with self.lock:  # Ensure thread-safe modification of commands and flags
            Logger().info(f"BeaconManager updating commands, new commands size: {len(new_commands)}, is_repetitive: {is_repetitive}")
            self.is_repetitive = is_repetitive
            self.original_commands = new_commands[:]  # Store a copy of the new commands

            # Clear the queue before adding new commands to ensure immediate processing
            while not self.commands_queue.empty():
                self.commands_queue.get()
                self.commands_queue.task_done()

            for command in new_commands:
                self.commands_queue.put(command)  # Add new commands to the queue

    def stop(self):
        Logger().info("BeaconManager stopping...")
        self._thread.join()  # Ensure the thread finishes processing
        Logger().info("BeaconManager stopped")

    def start(self):
        if not self._thread.is_alive():
            Logger().info("BeaconManager starting...")
            self._thread = Thread(target=self.run, args=())
            self._thread.start()
            Logger().info("BeaconManager started")