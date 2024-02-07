beacon_mac_address = "F7 C4 BB BE EF 49"
command_start = "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 04 03 03 9A FE 16 16 9A FE 20 00 0A DA 64 00 00 00 00 05 "
beacon_mac_as_bytes = beacon_mac_address.replace(":", " ")
command_end = " BB BB BB"

full_command = command_start + beacon_mac_as_bytes + command_end

