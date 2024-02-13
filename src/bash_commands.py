beacon_mac_address = "F7 C4 BB BE EF 49"
command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "
beacon_mac_as_bytes = beacon_mac_address.replace(":", " ")
command_end = " BB BB BB"

full_command = command_start + beacon_mac_as_bytes + command_end



# def process_events(events_json):
#     events_data = json.loads(events_json)

#     command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "
#     command_end = " BB BB BB"

#     for event in events_data['events']:
#         if 'mac_address' in event:
#             mac_address = event['mac_address']
#             wait_time = event['wait_time']
#             beacon_mac_as_bytes = mac_address.replace(":", " ")
#             full_command = command_start + beacon_mac_as_bytes + command_end

#             print("Sending command for beacon:", mac_address)
#             print(full_command)
#             print("Waiting for", wait_time, "seconds...\n")
#             time.sleep(wait_time)  # Simulate waiting
#         elif 'break_duration' in event:
#             break_duration = event['break_duration']
#             print("Turning off Bluetooth for", break_duration, "seconds...")
#             time.sleep(break_duration)  # Simulate break
#             print("Turning Bluetooth back on...\n")