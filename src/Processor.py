#!/usr/bin/env python

from collections import defaultdict

from Instruction import Instruction
from Memory import Memory
from RegisterFile import RegisterFile

class Processor (object):
    fetcher_buffer = {}
    reg_fetcher_buffer = {}
    executor_buffer = {}
    memory_buffer = {}


    def __init__ (self, memory, start_address):
        self.memory= memory
        self.data_memory = defaultdict (lambda : 0)
        self.start_address = start_address
        self.register_file = RegisterFile ()
        self.PC = 0
        self.IR = ""
        self.NPC = 0

    def do_operation (self, opcode, oper1, oper2):
        oper_dict = {
            'ADD'  : ' +',
            'ADDI' : ' +',
            'SUB'  : ' -',
            'MUL'  : ' *',
            'DIV'  : ' /',
            'AND'  : ' &',
            'ANDI' : ' &',
            'OR'   : ' |',
            'ORI'  : ' |',
            'XOR'  : ' ^',
            'XORI' : ' ^',
            'NOR'  : '~|',
        }
        opr = oper_dict [opcode]
        expr = (opr [0] + '('
                + str (oper1) + opr [1] + str (oper2)
                + ')')
        return eval (expr)

    def fetchInstruction (self):
        try :
            self.IR = self.memory [self.PC]
            self.NPC = self.PC + 4
            return {'instr' : Instruction (self.IR)}
        except IndexError :
            return {}

    def decodeInstruction (self):
        if not self.fetcher_buffer.has_key ('instr') : return {}
        instr = self.fetcher_buffer ['instr']

        # R type : rd <- rs funct rt
        # If applicable, mark the output register in the registerfile
        # as dirty. And if the input registers are not dirty, then put
        # them in the buffer.
        if instr.type == 'R':
            if (self.register_file.isClean (instr.rs) and
                self.register_file.isClean (instr.rt)) :
                self.fetcher_buffer = {}
                return {
                    'instr' : instr,
                    'rs' : [instr.rs, self.register_file [instr.rs]],
                    'rt' : [instr.rt, self.register_file [instr.rt]]
                }
            self.register_file.setDirty (instr.rd)
            return {}

        # I type : rt <- rs funct imm
        # I type load : rt <- mem [imm (rs)]
        elif (instr.type == 'I' and (len (instr.opcode) == 4 or
                                     instr.opcode [0] == 'L')):
            if self.register_file.isClean (instr.rs) :
                self.fetcher_buffer = {}
                return {
                    'instr' : instr,
                    'rs' : [instr.rs, self.register_file [instr.rs]],
                    'immediate' : instr.immediate
                }
            self.register_file.setDirty (instr.rt)
            return {}

        # I type store: mem [imm (rs)] <- rt
        # I type branch: jump to imm depending on comparison of rs and rt
        elif (instr.type == 'I' and instr.opcode [0] in 'SB'):
            if (self.register_file.isClean (instr.rs) and
                self.register_file.isClean (instr.rt)):
                self.fetcher_buffer = {}
                return {
                    'instr' : instr,
                    'rs' : [instr.rs, self.register_file [instr.rs]],
                    'rt' : [instr.rt, self.register_file [instr.rt]],
                    'immediate' : instr.immediate
                }
            return {}

        elif instr.type == 'J':
            # take 4 msb of PC
            # mul imm by 4
            # concatenate
            # That's where we should jump
            pc_msb = bin (self.PC) [2:].zfill (32) [:4]
            imm = bin (instr.immediate * 4) [2:].zfill (28)
            jump_addr = int (pc_msb + imm, 2)
            self.fetcher_buffer = {}
            return {
                'instr' : instr,
                'jump_addr' : jump_address
            }

    def execute (self):
        if not self.reg_fetcher_buffer.has_key ('instr') : return {}
        instr = self.reg_fetcher_buffer ['instr']

        if instr.type == 'J':
            return self.reg_fetcher_buffer

        if instr.type == 'R':
            # Check if operands are in the buffer, if not, we need to
            # stall (or do some orperand forwarding stuff)
            if (self.reg_fetcher_buffer.has_key ('rs') and
                self.reg_fetcher_buffer.has_key ('rt')) :
                self.register_file [instr.rd] = self.do_operation (
                    instr.opcode,
                    self.reg_fetcher_buffer ['rs'] [1],
                    self.reg_fetcher_buffer ['rt'] [1]
                )
                self.reg_fetcher_buffer = {}
                return {'instr' : instr,
                        'rd' : [instr.rd,
                                self.register_file [instr.rd]]}
            # Here, we should take care of orperand fowarding
            else: return {}

        if instr.type == 'I':
            # Check if operands are in the buffer, if not, we need to
            # stall (or do some orperand forwarding stuff)
            if (self.reg_fetcher_buffer.has_key ('rs') and
                self.reg_fetcher_buffer.has_key ('immediate')) :
                # Immediate ALU operations
                if len (instr.opcode) == 4:
                    self.register_file [instr.rt] = self.do_operation (
                        instr.opcode,
                        self.reg_fetcher_buffer ['rs'] [1],
                        self.reg_fetcher_buffer ['immediate']
                    )
                    self.reg_fetcher_buffer = {}
                    return {'instr' : instr,
                            'rt' : [instr.rt,
                                    self.register_file [instr.rt]]}

                # Load  : rt <- mem [imm (rs)]
                if (len (instr.opcode) == 2 and
                    instr.opcode [0] in 'L') :
                    memaddr = (self.reg_fetcher_buffer ['rs'] [1]
                               +
                               self.reg_fetcher_buffer ['immediate'])
                    self.reg_fetcher_buffer = {}
                    return {'instr' : instr,
                            'rt' : instr.rt,
                            'memaddr' : memaddr}

                # Store : mem [imm (rs)] <- rt
                if (len (instr.opcode) == 2 and
                    instr.opcode [0] in 'S') :
                    memaddr = (self.reg_fetcher_buffer ['rs'] [1]
                               +
                               self.reg_fetcher_buffer ['immediate'])
                    self.reg_fetcher_buffer = {}
                    return {'instr' : instr,
                            'memaddr' : memaddr,
                            'rt' : [instr.rt,
                                    self.register_file [instr.rt]]}

            else: return {}
            # BEQ and BNE
            if (self.reg_fetcher_buffer.has_key ('rs') and
                self.reg_fetcher_buffer.has_key ('immediate') and
                self.reg_fetcher_buffer.has_key ('rt')) :
                condition_output = True
                if (len (instr.opcode) == 3 and
                    instr.opcode == 'BEQ') :
                    condition_output = (
                        self.reg_fetcher_buffer ['rs'] [1]
                        ==
                        self.reg_fetcher_buffer ['rt'] [1]
                    )
                elif (len (instr.opcode) == 3 and
                    instr.opcode == 'BNE') :
                    condition_output = not (
                        self.reg_fetcher_buffer ['rs'] [1]
                        ==
                        self.reg_fetcher_buffer ['rt'] [1]
                    )
                self.reg_fetcher_buffer = {}
                return {
                    'instr' : instr,
                    'condition_output' : condition_output,
                    'jump_addr': (
                        self.NPC +
                        4 * instr.immediate
                     )
                }
            else: return {}

    def doMemoryOperations (self):
        self.PC = self.NPC
        if not self.executor_buffer.has_key ('instr') : return {}
        instr = self.executor_buffer['instr']

        if instr.type == 'J':
            self.PC = self.executor_buffer ['jump_addr']
            return {}

        # Load  : rt <- mem [imm (rs)]
        if (len (instr.opcode) == 2 and
            instr.opcode [0] in 'L') :
            mem_val = self.data_memory [self.executor_buffer ['memaddr']]
            self.register_file [instr.rt] = mem_val
            self.executor_buffer = {}
            return {'instr' : instr,
                    'rt' : [instr.rt, mem_val]}

        # Store : mem [imm (rs)] <- rt
        elif (len (instr.opcode) == 2 and
            instr.opcode [0] in 'S') :
            self.data_memory [self.executor_buffer ['memaddr']] = (
                self.executor_buffer ['rt'] [1]
            )
            self.executor_buffer = {}
            return {'instr' : instr}

        elif instr.opcode in 'BNE BEQ':
            if self.executor_buffer ['condition_output']:
                self.PC = self.executor_buffer ['jump_addr']

        temp = self.executor_buffer
        self.executor_buffer = {}
        return temp

    def writeBackRegisters (self):
        if not self.memory_buffer.has_key ('instr') : return {}
        instr = self.memory_buffer ['instr']

        # Mark the output registers clean.
        if instr.type == 'R':
            self.register_file.setClean (instr.rd)
        elif instr.type == 'I':
            self.register_file.setClean (instr.rt)

        self.memory_buffer = {}

    def printBuffers (self):
        for buf in ['fetcher_buffer',
                    'reg_fetcher_buffer',
                    'executor_buffer',
                    'memory_buffer'] :
            print buf
            print self.__getattribute__ (buf)

    def start (self):
        self.instruction_addres = self.start_address
        self.more_instructions_to_fetch = True
        while (self.more_instructions_to_fetch):
            self.printBuffers ()
            print self.register_file
            foo = (
                self.writeBackRegisters (),
                self.doMemoryOperations () or self.memory_buffer,
                self.execute () or self.executor_buffer,
                self.decodeInstruction () or self.reg_fetcher_buffer,
                self.fetchInstruction () or self.fetcher_buffer,
            )
            (
                blah,
                self.memory_buffer,
                self.executor_buffer,
                self.reg_fetcher_buffer,
                self.fetcher_buffer,
            ) = foo
            self.more_instructions_to_fetch = (
                self.memory_buffer or
                self.executor_buffer or
                self.reg_fetcher_buffer or
                self.fetcher_buffer
            )

if __name__ == "__main__":
    memory = Memory ()
    # memory.loadProgram ('./Input_hex_fibonacci.txt')
    memory.loadProgramDebug ('./adder.txt')
    processor = Processor (memory, 0)
    processor.start ()
