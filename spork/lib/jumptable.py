"""

Jump table construct 

used to run code base on enumeration 

get jump ref as an integer

guard the integer size
- table 
ref1
ref2
ref3

ref1:
 code
 code 
 code
 J(end)

ref2:
 code
 code 
 code
 J(end)

end:

"""


class JumpTable:
    def __init__(self):
        self.commands = {}
