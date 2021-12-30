# instruction selector

from boneless.arch.opcode import * 
class InstructionSelector:
    def __init__(self):
        self.table = {
            ('add','int','const') : ADDI,
        }

    def select(self,find):
        print('find')
