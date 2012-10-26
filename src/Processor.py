#!/usr/bin/env python

from collections import defaultdict
import sys
from warnings import warn
from Instruction import Instruction
from Memory import Memory
from RegisterFile import RegisterFile
from pprint import pprint
import pickle

default_data_file_name =  'new-cycle-data.pickle'

class Processor (object):
    fetcher_buffer = {}
    decoder_buffer = {}
    executor_buffer = {}
    memory_buffer = {}

    decoder_stalled = False
    executor_stalled = False
    mem_stalled = False
    reg_writer_stalled = False

    data_memory_key_fn = lambda: 0

    def __init__ (self, memory, start_address):
        self.memory= memory
        self.data_memory = defaultdict (self.data_memory_key_fn)
        self.start_address = start_address
        self.register_file = RegisterFile ()
        self.PC = 0
        self.IR = ""
        self.NPC = 0
        self.cycle_count = 0
        self.instr_count= 0

    def do_operation (self, opcode, oper1, oper2):
        """Return value of arithmetic expression `oper1 opcode oper2`.
        """
        oper_dict = {
            'ADD' : ' +',
            'ADDI': ' +',
            'SUB' : ' -',
            'MUL' : ' *',
            'DIV' : ' /',
            'AND' : ' &',
            'ANDI': ' &',
            'OR'  : ' |',
            'ORI' : ' |',
            'XOR' : ' ^',
            'XORI': ' ^',
            'NOR' : '~|',
        }
        opr = oper_dict [opcode]
        expr = (opr [0] + '('
                + str (oper1) + opr [1] + str (oper2)
                + ')')
        return eval (expr)

    def fetch_instruction (self, fetch_input_buffer = None):
        """Based on PC value, fetch instruction from memory.

        Update PC.
        Return fetcher_buffer for the next cycle.

        Arguments:
        - fetch_input_buffer: contains
          + PC
          + memory
          + is_branch_reg_zero
          + branch_target_pc
          + is_decoder_stalled
          + register_file
          + instr_count

        TODO: Take in and pass on the register_file.
        """
        if fetch_input_buffer.get('is_decoder_stalled', False):
            return {}
        try:
            memory = fetch_input_buffer['memory']
            PC = fetch_input_buffer['PC']
            instr_count = fetch_input_buffer['instr_count']

            IR = memory [PC]

            # Is the NPC even needed anymore?
            # PC = NPC
            NPC = PC + 4
            print 'NPC changed to', NPC

            instr_count += 1
            return {'instr': Instruction (IR),
                    'npc': NPC,
                    'PC': PC}
        except IndexError:
            # warn('IndexError in fetchInstruction')
            return {}

    def fetchInstruction (self):
        """Based on PC value, fetch instruction from memory. Update PC.
        Return the value of the fetcher_buffer for the next cycle.
        """
        if self.decoder_stalled :
            return {}
        try :
            self.IR = self.memory [self.PC]
            self.NPC = self.PC + 4
            self.PC = self.NPC
            print 'self.NPC changed to', self.NPC

            self.instr_count += 1
            return {'instr' : Instruction (self.IR),
                    'npc' : self.NPC}
        except IndexError :
            print 'IndexError in fetchInstruction'
            return {}

    def decode_R_instruction(self, fetcher_buffer):
        """Return decoder_buffer given fetcher_buffer.

        R type: rd <- rs funct rt
        If applicable, mark the output register in the registerfile
        as dirty. And if the input registers are not dirty, then put
        them in the buffer.

        decoder_buffer contains:
        + modified register_file
        + next fetcher_buffer
        + instr
        + rs
        + rt
        + npc
        + is_decoder_stalled

        Arguments:
        - `fetcher_buffer`: contains
          + register_file
          + instr
          + npc
        """
        register_file = fetcher_buffer['register_file']
        instr = fetcher_buffer ['instr']
        npc = fetcher_buffer ['npc']
        is_decoder_stalled = False

        if (register_file.isClean (instr.rs) and
            register_file.isClean (instr.rt)):

            fetcher_buffer = {}
            register_file.setDirty (instr.rd)

            return {
                'register_file': register_file,
                'fetcher_buffer': fetcher_buffer,
                'is_decoder_stalled': is_decoder_stalled,
                'instr': instr,
                'rs': [instr.rs, register_file [instr.rs]],
                'rt': [instr.rt, register_file [instr.rt]],
                'npc': npc,
                }
        else:
            is_decoder_stalled = True
            register_file.setDirty (instr.rd)
            return {
                'register_file': register_file,
                'fetcher_buffer': fetcher_buffer,
                'is_decoder_stalled': is_decoder_stalled,
            }

    def decode_I_instruction(self, fetcher_buffer):
        """Return decoder_buffer given fetcher_buffer.

        I type: rt <- rs funct imm
        I type load: rt <- mem [imm (rs)]
        I type store: mem [imm (rs)] <- rt
        I type branch: jump to imm depending on comparison of rs and rt

        decoder_buffer contains:
        + modified register_file
        + next fetcher_buffer
        + instr
        + rs
        + rt
        + npc
        + is_decoder_stalled

        Arguments:
        - `fetcher_buffer`: contains
          + register_file
          + instr
          + npc
        """
        register_file = fetcher_buffer['register_file']
        instr = fetcher_buffer ['instr']
        npc = fetcher_buffer ['npc']
        is_decoder_stalled = False

        # I type: rt <- rs funct imm
        # I type load: rt <- mem [imm (rs)]
        if (instr.type == 'I' and instr.opcode in [
                'ADDI', 'ANDI', 'ORI', 'XORI', 'LB', 'LW']):
            if register_file.isClean (instr.rs):
                fetcher_buffer = {}
                register_file.setDirty (instr.rt)
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                    'instr': instr,
                    'rs': [instr.rs, register_file [instr.rs]],
                    'npc': npc,
                    'immediate': instr.immediate
                    }
            else:
                is_decoder_stalled = True
                register_file.setDirty (instr.rt)
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                    }

        # I type store: mem [imm (rs)] <- rt
        # I type branch: jump to imm depending on comparison of rs and rt
        elif (instr.type == 'I' and instr.opcode [0] in ['SB', 'BEQ', 'SW', 'BNE']):
            if (register_file.isClean (instr.rs) and
                register_file.isClean (instr.rt)):
                fetcher_buffer = {}
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                    'instr': instr,
                    'rs': [instr.rs, register_file [instr.rs]],
                    'rt': [instr.rt, register_file [instr.rt]],
                    'npc': npc,
                    'immediate': instr.immediate
                }
            else:
                is_decoder_stalled = True
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                }

    def decodeInstruction (self):
        """Decode the instr in fetcher_buffer and read from registers.

        Check for possible branch. Compute branch target address, if
        needed.

        Also, update the PC to the computed branch target.

        Return decoder_buffer.

        Remove references to fetcher_buffer. I think it is only
        emptied when there is NO decode stall. That logic should be in
        the code that drives the stages.
        """
        if self.executor_stalled: return {}
        if not self.fetcher_buffer.has_key ('instr'): return {}
        instr = self.fetcher_buffer ['instr']
        npc = self.fetcher_buffer ['npc']
        self.decoder_stalled = False

        # R type: rd <- rs funct rt
        # If applicable, mark the output register in the registerfile
        # as dirty. And if the input registers are not dirty, then put
        # them in the buffer.
        if instr.type == 'R':
            if (self.register_file.isClean (instr.rs) and
                self.register_file.isClean (instr.rt)):
                self.fetcher_buffer = {}
                self.register_file.setDirty (instr.rd)
                return {
                    'instr': instr,
                    'rs': [instr.rs, self.register_file [instr.rs]],
                    'rt': [instr.rt, self.register_file [instr.rt]],
                    'npc': npc,
                }
            else:
                self.decoder_stalled = True
                self.register_file.setDirty (instr.rd)
                return {}
            pass
        # I type: rt <- rs funct imm
        # I type load: rt <- mem [imm (rs)]
        elif (instr.type == 'I' and (len (instr.opcode) == 4 or
                                     instr.opcode [0] == 'L')):
            if self.register_file.isClean (instr.rs):

                # TODO: Why is this here?
                self.fetcher_buffer = {}
                self.register_file.setDirty (instr.rt)
                return {
                    'instr': instr,
                    'rs': [instr.rs, self.register_file [instr.rs]],
                    'npc': npc,
                    'immediate': instr.immediate
                }
            else:
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
                    'instr': instr,
                    'rs': [instr.rs, self.register_file [instr.rs]],
                    'rt': [instr.rt, self.register_file [instr.rt]],
                    'npc': npc,
                    'immediate': instr.immediate
                }
            else:
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
        if self.mem_stalled: return {}
        if not self.decoder_buffer.has_key ('instr'): return {}
        instr = self.decoder_buffer ['instr']
        npc = self.decoder_buffer ['npc']

        self.executor_stalled = False
        if instr.type == 'J':
            return self.decoder_buffer

        if instr.type == 'R':
            # Check if operands are in the buffer, if not, we need to
            # stall (or do some orperand forwarding stuff)
            if (self.decoder_buffer.has_key ('rs') and
                self.decoder_buffer.has_key ('rt')):
                self.register_file [instr.rd] = self.do_operation (
                    instr.opcode,
                    self.decoder_buffer ['rs'] [1],
                    self.decoder_buffer ['rt'] [1]
                )
                self.decoder_buffer = {}
                return {'instr': instr,
                        'npc': npc,
                        'rd': [instr.rd,
                                self.register_file [instr.rd]]}
            # Here, we should take care of orperand fowarding
            else:
                self.executor_stalled = True
                return {}

        if instr.type == 'I':
            # Check if operands are in the buffer, if not, we need to
            # stall (or do some orperand forwarding stuff)
            if (self.decoder_buffer.has_key ('rs') and
                self.decoder_buffer.has_key ('immediate')):
                # Immediate ALU operations
                if len (instr.opcode) == 4:
                    self.register_file [instr.rt] = self.do_operation (
                        instr.opcode,
                        self.decoder_buffer ['rs'] [1],
                        self.decoder_buffer ['immediate']
                    )
                    self.decoder_buffer = {}
                    return {'instr': instr,
                            'npc': npc,
                            'rt': [instr.rt,
                                    self.register_file [instr.rt]]}

                # Load : rt <- mem [imm (rs)]
                if (len (instr.opcode) == 2 and
                    instr.opcode [0] in 'L'):
                    memaddr = (self.decoder_buffer ['rs'] [1]
                               +
                               self.decoder_buffer ['immediate'])
                    self.decoder_buffer = {}
                    return {'instr': instr,
                            'npc': npc,
                            'rt': instr.rt,
                            'memaddr': memaddr}

                # Store: mem [imm (rs)] <- rt
                if (len (instr.opcode) == 2 and
                    instr.opcode [0] in 'S'):
                    memaddr = (self.decoder_buffer ['rs'] [1]
                               +
                               self.decoder_buffer ['immediate'])
                    self.decoder_buffer = {}
                    return {'instr': instr,
                            'npc': npc,
                            'memaddr': memaddr,
                            'rt': [instr.rt,
                                    self.register_file [instr.rt]]}

            else:
                self.executor_stalled = True
                return {}
            # BEQ and BNE
            if (self.decoder_buffer.has_key ('rs') and
                self.decoder_buffer.has_key ('immediate') and
                self.decoder_buffer.has_key ('rt')):
                condition_output = True
                if (len (instr.opcode) == 3 and
                    instr.opcode == 'BEQ'):
                    condition_output = (
                        self.decoder_buffer ['rs'] [1]
                        ==
                        self.decoder_buffer ['rt'] [1]
                    )
                elif (len (instr.opcode) == 3 and
                    instr.opcode == 'BNE'):
                    condition_output = not (
                        self.decoder_buffer ['rs'] [1]
                        ==
                        self.decoder_buffer ['rt'] [1]
                    )
                self.decoder_buffer = {}
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
        if self.reg_writer_stalled: return {}
        if not self.executor_buffer.has_key ('instr'): 
            print 'Should PC have been changed here??'
            return {}
        instr = self.executor_buffer['instr']

        # Load : rt <- mem [imm (rs)]
        if (len (instr.opcode) == 2 and
            instr.opcode [0] in 'L'):
            mem_val = self.data_memory [self.executor_buffer ['memaddr']]
            self.register_file [instr.rt] = mem_val
            self.executor_buffer = {}
            return {'instr': instr,
                    'rt': [instr.rt, mem_val]}

        # Store: mem [imm (rs)] <- rt
        elif (len (instr.opcode) == 2 and
            instr.opcode [0] in 'S'):
            self.data_memory [self.executor_buffer ['memaddr']] = (
                self.executor_buffer ['rt'] [1]
            )
            self.executor_buffer = {}
            return {'instr': instr}

        temp = self.executor_buffer
        self.executor_buffer = {}
        return temp

    def writeBackRegisters (self):
        if not self.memory_buffer.has_key ('instr'): return {}
        instr = self.memory_buffer ['instr']

        # Mark the output registers clean.
        if instr.type == 'R':
            self.register_file.setClean (instr.rd)
        elif instr.type == 'I':
            self.register_file.setClean (instr.rt)

        self.memory_buffer = {}

    def printBuffers (self):
        print "PC:", self.PC
        for buf in ['fetcher_buffer',
                    'decoder_buffer',
                    'executor_buffer',
                    'memory_buffer']:
            print buf
            print self.__getattribute__ (buf)

    def get_all_curr_data(self):
        """Return dict of all data in the Processor at the moment.
        """

        # TODO: It gives 'Can't pickle instancemethod object' error
        # when I have self.data_memory too.

        curr_data_dict = {
            'fetcher_buffer': self.fetcher_buffer,
            'decoder_buffer': self.decoder_buffer,
            'executor_buffer': self.executor_buffer,
            'memory_buffer': self.memory_buffer,
            'decoder_stalled': self.decoder_stalled,
            'executor_stalled': self.executor_stalled,
            'mem_stalled': self.mem_stalled,
            'reg_writer_stalled': self.reg_writer_stalled,
            'memory': self.memory,
            'start_address': self.start_address,
            'register_file': self.register_file,
            'PC': self.PC,
            'IR': self.IR,
            'NPC': self.NPC,
            'cycle_count': self.cycle_count,
            'instr_count': self.instr_count,
            }
        return curr_data_dict

    @staticmethod
    def save_cycle_data(cycle_data_list, cycle_data_file_name = default_data_file_name):
        """Pickle and save cycle_data_list.
        
        Arguments:
        - `cycle_data_list`:
        """

        with open(cycle_data_file_name, 'w') as f:
            pickle.dump(cycle_data_list, f)

        print 'Wrote cycle_data_list to {0}'.format(cycle_data_file_name)

    @staticmethod
    def read_saved_data(cycle_data_file_name = default_data_file_name):
        """Return cycle data list saved in cycle_data_file_name.
        
        Arguments:
        - `cycle_data_file_name`:
        """
        cycle_data_list = []
        with open(cycle_data_file_name, 'rb') as f:
            cycle_data_list = pickle.load(f)
            print 'Read cycle_data_list from {0}'.format(cycle_data_file_name)
        return cycle_data_list


    def start(self, cycle_data_file_name = default_data_file_name):
        """Start execution of instructions from the start_address.
        """
        self.instruction_addres = self.start_address
        self.more_instructions_to_fetch = True

        # 1-based list of stuff generated at the end of each cycle.
        cycle_data_list = [None,]

        while (self.more_instructions_to_fetch):
            self.cycle_count += 1
            print 'Beginning of Cycle #' + str(self.cycle_count)
            print '=' * 12

            cycle_data_list.append(self.get_all_curr_data())

            self.printBuffers ()
            print self.register_file

            # TODO: Make it such that you run them in reverse order
            # and pass along the is_X_stalled value to the previous
            # pipeline stage.

            self.writeBackRegisters ()
            self.memory_buffer = self.doMemoryOperations () or self.memory_buffer
            self.executor_buffer = self.execute () or self.executor_buffer
            self.decoder_buffer = self.decodeInstruction () or self.decoder_buffer

            fetch_input_buffer = {
                'PC': self.PC,
                'memory': self.memory,
                'is_decoder_stalled': self.decoder_stalled,
                'instr_count': self.instr_count,
                }
            gen_fetcher_buffer = self.fetch_instruction (fetch_input_buffer) or self.fetcher_buffer
            # self.fetcher_buffer = self.fetch_instruction (fetch_input_buffer) or self.fetcher_buffer
            self.fetcher_buffer = self.fetchInstruction() or self.fetcher_buffer

            if gen_fetcher_buffer != self.fetcher_buffer:
                print 'gen_fetcher_buffer'
                pprint(gen_fetcher_buffer)
                print 'self.fetcher_buffer'
                pprint(self.fetcher_buffer)
                

            self.more_instructions_to_fetch = (
                self.memory_buffer or
                self.executor_buffer or
                self.decoder_buffer or
                self.fetcher_buffer
            )

        self.save_cycle_data(cycle_data_list, cycle_data_file_name)

    def getCPI (self):
        return (1.0 * self.cycle_count) / self.instr_count

if __name__ == "__main__":
    memory = Memory ()
    filename = './fibo.txt'
    if len (sys.argv) > 1:
        filename = sys.argv [1]
    memory.loadProgramDebug (filename)
    processor = Processor (memory, 0)
    processor.start ()
    print processor.getCPI ()
