#!/usr/bin/env python

from collections import defaultdict
import sys

from Instruction import Instruction
from Memory import Memory
from RegisterFile import RegisterFile

class Processor (object):
    fetcher_buffer = {}
    reg_fetcher_buffer = {}
    executor_buffer = {}
    memory_buffer = {}

    decoder_stalled = False
    executor_stalled = False
    mem_stalled = False
    reg_writer_stalled = False


    def __init__ (self, memory, start_address):
        self.memory= memory
        self.data_memory = defaultdict (lambda : 0)
        self.start_address = start_address
        self.register_file = RegisterFile ()
        self.PC = 0
        self.IR = ""
        self.NPC = 0
        self.cycle_count = 0
        self.instr_count= 0

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
        """Based on PC value, fetch instruction from memory. Update PC.
        Return the value of the fetcher_buffer for the next cycle.
        """
        if self.decoder_stalled :
            return {}
        try :
            self.instr_count += 1
            self.IR = self.memory [self.PC]
            self.NPC = self.PC + 4
            self.PC = self.NPC
            print 'self.NPC changed to', self.NPC

            return {'instr' : Instruction (self.IR),
                    'npc' : self.NPC}
        except IndexError :
            print 'IndexError in fetchInstruction'
            return {}

    def decodeInstruction (self):
        """Decode the instr in fetcher_buffer and read from registers.

        Check for possible branch. Compute branch target address, if
        needed.

        Also, update the PC to the computed branch target.
        """
        if self.executor_stalled : return {}
        if not self.fetcher_buffer.has_key ('instr') : return {}
        instr = self.fetcher_buffer ['instr']
        npc = self.fetcher_buffer ['npc']

        # R type : rd <- rs funct rt
        # If applicable, mark the output register in the registerfile
        # as dirty. And if the input registers are not dirty, then put
        # them in the buffer.
        self.decoder_stalled = False
        if instr.type == 'R':
            if (self.register_file.isClean (instr.rs) and
                self.register_file.isClean (instr.rt)) :
                self.fetcher_buffer = {}
                self.register_file.setDirty (instr.rd)
                return {
                    'instr' : instr,
                    'rs' : [instr.rs, self.register_file [instr.rs]],
                    'rt' : [instr.rt, self.register_file [instr.rt]],
                    'npc' : npc,
                }
            else :
                self.decoder_stalled = True
                self.register_file.setDirty (instr.rd)
                return {}

        # I type : rt <- rs funct imm
        # I type load : rt <- mem [imm (rs)]
        elif (instr.type == 'I' and (len (instr.opcode) == 4 or
                                     instr.opcode [0] == 'L')):
            if self.register_file.isClean (instr.rs) :
                self.fetcher_buffer = {}
                self.register_file.setDirty (instr.rt)
                return {
                    'instr' : instr,
                    'rs' : [instr.rs, self.register_file [instr.rs]],
                    'npc' : npc,
                    'immediate' : instr.immediate
                }
            else :
                self.decoder_stalled = True
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
                    'npc' : npc,
                    'immediate' : instr.immediate
                }
            else :
                self.decoder_stalled = True
                return {}

        elif instr.type == 'J':
            # take 4 msb of PC
            # mul offset_from_pc by 4
            # concatenate
            # That's where we should jump

            # TODO: Check this
            pc_msb = bin (npc - 4) [2:].zfill (32) [:4]
            # pc_msb = bin (self.PC) [2:].zfill (32) [:4]
            imm = bin (instr.offset_from_pc * 4) [2:].zfill (28)
            jump_addr = int (pc_msb + imm, 2)
            self.fetcher_buffer = {}
            self.PC = jump_addr
            return {}

    def execute (self):
        """
        """
        if self.mem_stalled : return {}
        if not self.reg_fetcher_buffer.has_key ('instr') : return {}
        instr = self.reg_fetcher_buffer ['instr']
        npc = self.reg_fetcher_buffer ['npc']

        self.executor_stalled = False
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
                        'npc' : npc,
                        'rd' : [instr.rd,
                                self.register_file [instr.rd]]}
            # Here, we should take care of orperand fowarding
            else:
                self.executor_stalled = True
                return {}

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
                            'npc' : npc,
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
                            'npc' : npc,
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
                            'npc' : npc,
                            'memaddr' : memaddr,
                            'rt' : [instr.rt,
                                    self.register_file [instr.rt]]}

            else:
                self.executor_stalled = True
                return {}
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
                if condition_output:
                    self.PC = npc + 4 * instr.immediate
                    print 'BNE/BEQ: PC changed to', self.PC
                return {}
            else: return {}

    def doMemoryOperations (self):
        # TODO: This is where the old code did the right thing. It set
        # PC to NPC before this line and in the cases where 'instr'
        # was not in executor_buffer, the new code would simply return
        # {} and cup.
        if self.reg_writer_stalled : return {}
        if not self.executor_buffer.has_key ('instr') : 
            print 'Should PC have been changed here??'
            return {}
        instr = self.executor_buffer['instr']

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
        print "PC :", self.PC
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
            self.cycle_count += 1
            print 'Beginning of Cycle #' + str(self.cycle_count)
            print '=' * 12

            self.printBuffers ()
            # print
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

    def getCPI (self):
        return (1.0 * self.cycle_count) / self.instr_count

if __name__ == "__main__":
    memory = Memory ()
    filename = './fibo.txt'
    if len (sys.argv) > 1 :
        filename = sys.argv [1]
    memory.loadProgramDebug (filename)
    processor = Processor (memory, 0)
    processor.start ()
    print processor.getCPI ()
