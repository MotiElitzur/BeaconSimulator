import time
from threading import Thread, Event
from Logger import Logger
import subprocess

class BeaconManager:

    logger = Logger()

    def __init__(self, is_repetitive=False):
        self._events = None
        self.events_updated = Event()
        self.is_repetitive = is_repetitive  # New attribute to control repetition

        self._thread = Thread(target=self.run, args=())
        self._thread.start()

    def run(self):

        while True:
            Logger().info("BeaconManager start waiting for events...")
            self.events_updated.wait()  # Wait until events are updated
            self.events_updated.clear()  # Reset the event flag after receiving events

            Logger().info("BeaconManager received new events")

            while True:  # Outer loop for handling repetition
                for event in self._events:
                    duration = event.get('duration', 0)  # Using a consistent name for duration

                    if event.get('type') == 'beacon_command':
                        mac_address = event['mac_address']
                        beacon_mac_as_bytes = mac_address.replace(":", " ")
                        command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "  # Adjusted to include a more generic company identifier
                        command_end = " BB BB BB"
                        full_command = command_start + beacon_mac_as_bytes + command_end

                        self.logger.info(f"Sending command for beacon: {mac_address}")
                        self.logger.info(full_command)
                        # Execute the full command
                        try:
                            subprocess.run(full_command, shell=True, check=True)
                            self.logger.info("Command executed successfully.")
                        except subprocess.CalledProcessError as e:
                            self.logger.error(f"Failed to execute command: {e}")

                        self.logger.info(f"Waiting for {duration} seconds...\n")
                        time.sleep(duration)

                    elif event.get('type') == 'break_event':
                        # Turning Bluetooth off
                        self.logger.info("Turning off Bluetooth...")
                        subprocess.run('sudo hciconfig hci0 down', shell=True, check=True)
                        time.sleep(duration)
                        # Turning Bluetooth back on
                        self.logger.info("Turning Bluetooth back on...")
                        subprocess.run('sudo hciconfig hci0 up', shell=True, check=True)

                    else:
                        self.logger.error("Unknown event type.")

                if not self.is_repetitive:
                    break  # Exit the outer loop if not repetitive, ending the event processing


    def update_events(self, new_events, is_repetitive=False):
        # Update the events and the is_repetitive flag here
        self._events = new_events
        self.is_repetitive = is_repetitive  # Update the repetitive flag based on new input
        self.events_updated.set()  # Notify the run method that events have been updated

    # def __init__(self):
    #     self._events = None
    #     self.events_updated = Event()

    #     self._thread = Thread(target=self.run, args=())
    #     self._thread.start()
        

    # def run(self):
    #     while True:
        
    #         Logger().info("BeaconManager start waiting for events...")
    #         self.events_updated.wait()  # Wait until events are updated

    #         Logger().info("BeaconManager received new events")
    #         self.events_updated
        
    #         for event in self._events:
    #             #  If the event is a beacon command event - send the command
    #             if 'mac_address' in event:
    #                 mac_address = event['mac_address']
    #                 beacon_mac_as_bytes = mac_address.replace(":", " ")
    #                 wait_time = event['wait_time']

    #                 command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "
    #                 command_end = " BB BB BB"

    #                 # TODO: Replace the following lines with the actual command sending code
    #                 full_command = command_start + beacon_mac_as_bytes + command_end

    #                 self.logger.info(f"Sending command for beacon: {mac_address}")
    #                 self.logger.info(full_command)
    #                 self.logger.info(f"Waiting for {wait_time} seconds...\n")
    #                 time.sleep(wait_time)
    #             else:  # If the event is a break event - turn off Bluetooth
    #                 break_duration = event['break_duration']
    #                 self.logger.info(f"Turning off Bluetooth for {break_duration} seconds...")
    #                 time.sleep(break_duration)
    #                 self.logger.info("Turning Bluetooth back on...\n")

    # def update_events(self, new_events):
    #     # Update the events here
    #     self._events = new_events
    #     self.events_updated.set()  # Notify the run method that events have been updated
        





#         import queue
# import threading
# import time

# class BeaconManager:
#     def __init__(self):
#         self.event_queue = queue.Queue()
#         self.keep_running = True  # Flag to control the running of the thread
#         self.worker_thread = threading.Thread(target=self.process_events)
#         self.worker_thread.start()

#     def process_events(self):
#         while self.keep_running:
#             try:
#                 event = self.event_queue.get(timeout=3)  # Adjust timeout as needed
#                 if event is None:
#                     break  # None is used as a signal to stop the thread
#                 # Process the event
#                 print(f"Processing event: {event}")
#                 # Example processing code here...
                
#             except queue.Empty:
#                 continue  # Timeout reached, loop again to check keep_running

#         print("Event processing thread terminating.")

#     def enqueue_event(self, event):
#         self.event_queue.put(event)

#     def stop(self):
#         self.keep_running = False
#         self.event_queue.put(None)  # Signal the thread to exit
#         self.worker_thread.join()

# # Example usage
# beacon_manager = BeaconManager()
# beacon_manager.enqueue_event({"type": "beacon_command", "details": "Command details"})
# # When ready to stop
# beacon_manager.stop()
