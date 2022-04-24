# Monitor overview

 Create a interactive monitor program. This should enable running, interrogating and modifying a firware from within the python console. 

- General structure stolen from
-  https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/gateware/bootloader_fw.py
- a extensible serial monitor

# Command / Response packet based serial connection 

Each Packet consists of 
- magic number 16bit (0x5A04 for now see MAGIC in commands)
- command ( use Enum )
- parameter 1
- parameter 2
- checksum 

if the command has data attached

- data , data , data , data 
- status
- checksum of data

# Possible commands 

use enum and expandable jumptable ; 

if check item < length jump error
store 'jvt end' in R7 , return register
jump through table 

- hello ; liveness check
- host_info ; some version and gateway information
- heart_beat ; a heartbeat event (monotonic counter)
- write_data ; datablock write
- read_data ; datablock read 
- jump ; jump to address and execute

- read external ; read peripheral data 
- write external ; write peripheral data 

- load code ; loads new code into the monitor ( add to this table)
- delete code ; delete code , free memory and delete from this table
- list code ; list the set of loaded code blocks

- watch ; add code that is run every cycle
- unwatch ; remove watch 
- notify ; send a packet when a value changes

- reset ; reset the monitor 
- core dump ; dump the entire memory
- unwind stack ; harder than it looks
- breakpoint ; set and remove
- ... other 
  - object load
  - object save
  - file system 
    - read
    - write
    - delete
    - open 
    - etc


ends with label('jvt end'), code 

# Response Codes 

- hello_response ( possibly olleh :) hehe )
- ok
- crc_error
- data_error
- heart_beat
# Transaction 
Coded as two byte words, Command followed by response
## Example hello packet
send |> MAGIC  , HELLO , 0 , 0 , CHECKSUM

recieve <| MAGIC , HELLO_RESP , 0 , 0 , CHECKSUM

# Firmware and Code infrastructure.

Both host and firmware sides are encapsulated and extensable. A single class file should contain host and soc code, adding a new command should just be a new class that is attached.
- ## Host Side
  - Connection and error handling is transparent.
  - Check capability of monitor firmware and send updated codes and functions.
  - Update assembler to have all symbols and register names available.
- ## Client side
  - Main loop check for serial port
