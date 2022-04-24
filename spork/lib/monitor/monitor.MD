# create a interactive monitor program

# General structure stolen from
# https://github.com/tpwrules/tasha_and_friends/blob/master/tasha/gateware/bootloader_fw.py

# a extensible serial monitor

# Command / Response packet based serial connection 

Each Packet consists of 
- magic number 16bit (0x5A04 for now see MAGIC in commands)
- command ( use Enum )
- parameter 1
- parameter 2
- checksum 

if the command has data attached

- data , data , data , data 
- checksum of data

# Possible commands 

use enum and expandable jumptable ; 

if check item < length jump error
store 'jvt end' in R7 , return register
jump through table 

- hello ; liveness check

- write data ; datablock write
- read data ; datablock read 
- jump ; jump to address and execute

- read external ; read peripheral data 
- write external ; write peripheral data 

- load code ; loads new code into the monitor ( add to this table)
- delete code ; delete code , free memory and delete from this table
- list code ; list the set of loaded code blocks

- watch ; add code that is run every cycle

- reset ; reset the monitor 
- core dump ; dump the entire memory
- unwind stack 
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


label('jvt end')
"""

# 