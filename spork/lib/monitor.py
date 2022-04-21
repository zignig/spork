# create a interactive monitor program

# General structure stolen from
# https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/gateware/bootloader_fw.py

# a extensible serial monitor

"""
Command / Response packet based serial connection 

Each Packet consists of 
- magic number 16bit
- command ( use Enum )
- parameter 1
- parameter 2
- checksum 

if the command has data attached
- data , data , data , data 
- checksum of data

# 
"""
