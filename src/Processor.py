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

    @staticmethod
    def do_operation (opcode, oper1, oper2):
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

    # def fetchInstruction (self):
    #     """Based on PC value, fetch instruction from memory. Update PC.
    #     Return the value of the fetcher_buffer for the next cycle.
    #     """
    #     if self.decoder_stalled :
    #         return {}
    #     try :
    #         self.IR = self.memory [self.PC]
    #         self.NPC = self.PC + 4
    #         self.PC = self.NPC
    #         print 'self.NPC changed to', self.NPC

    #         self.instr_count += 1
    #         return {'instr' : Instruction (self.IR),
    #                 'npc' : self.NPC}
    #     except IndexError :
    #         print 'IndexError in fetchInstruction'
    #         return {}

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
        elif (instr.type == 'I' and instr.opcode in ['SB', 'BEQ', 'SW', 'BNE']):
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
        
    @staticmethod
    def get_jump_address(npc, instr):
        """Return jump address for instr given npc.

        Take 4 msb of old PC
        Mul offset_from_pc by 4
        Concatenate
        That's where we should jump

        Arguments:
        - `instr`: J-type instruction.
        """
        old_pc = npc - 4
        pc_msb = Memory.get_binary_string(old_pc)[:4]
        imm = Memory.get_binary_string(instr.offset_from_pc * 4, 28)
        jump_addr = int (pc_msb + imm, 2)
        return jump_addr
        
    def decode_J_instruction(self, fetcher_buffer):
        """Return decoder_buffer given fetcher_buffer.

        J type instruction

        decoder_buffer contains:
        + register_file
        + next fetcher_buffer
        + instr
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

        fetcher_buffer = {}
        PC = self.get_jump_address(npc, instr)
        print 'npc: ', npc
        print 'jump_addr: ', PC

        return {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': is_decoder_stalled,
            'instr': instr,
            'npc': npc,
            'PC': PC,
            }

    def decode_instruction (self, fetcher_buffer):
        """Decode the instr in fetcher_buffer and read from registers.

        Check for possible branch. Compute branch target address, if
        needed.

        Also, update the PC to the computed branch target.

        Return decoder_buffer.
        """
        if fetcher_buffer.get('is_executor_stalled', False): 
            return {}
        if not fetcher_buffer.has_key ('instr'): 
            return {}

        instr = fetcher_buffer['instr']
        if instr.type == 'R':
            return self.decode_R_instruction(fetcher_buffer)
        elif instr.type == 'I':
            return self.decode_I_instruction(fetcher_buffer)
        elif instr.type == 'J':
            return self.decode_J_instruction(fetcher_buffer)

    def execute_R_instruction(self, decoder_buffer):
        """Execute the R instruction and update the register file.

        Return mem_buffer.

        mem_buffer contains:
        + register_file
        + next decoder_buffer
        + instr
        + npc
        + is_executor_stalled
        
        Arguments:
        - `decoder_buffer`:
          + instr
          + npc
          + register_file
          + is_mem_stalled
        """
        instr = decoder_buffer['instr']
        register_file = decoder_buffer['register_file']
        npc = decoder_buffer['npc']
        is_executor_stalled = False

        # Check if operands are in the buffer
        if (decoder_buffer.has_key ('rs') and
            decoder_buffer.has_key ('rt')):
            register_file [instr.rd] = self.do_operation (
                instr.opcode,
                decoder_buffer ['rs'] [1],
                decoder_buffer ['rt'] [1]
                )
            decoder_buffer = {}
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                'instr': instr,
                'npc': npc,
                'rd': [instr.rd, register_file [instr.rd]],
                }
        else:
            # Here, we should take care of operand fowarding
            is_executor_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                }
        
    def execute_I_instruction(self, decoder_buffer):
        """Execute the I instruction and update the register file.

        Return mem_buffer.

        mem_buffer contains:
        + register_file
        + next decoder_buffer
        + is_executor_stalled
        + instr
        + npc
        + rt
        + memaddr (optional)
        
        Arguments:
        - `decoder_buffer`:
          + instr
          + npc
          + register_file
          + is_mem_stalled
        """
        instr = decoder_buffer['instr']
        register_file = decoder_buffer['register_file']
        npc = decoder_buffer['npc']
        is_executor_stalled = False

        # Check if operands are in the buffer.
        if (decoder_buffer.has_key ('rs') and
            decoder_buffer.has_key ('immediate')):
            # Immediate ALU operations
            if len (instr.opcode) == 4:
                register_file [instr.rt] = self.do_operation (
                    instr.opcode,
                    decoder_buffer ['rs'] [1],
                    decoder_buffer ['immediate']
                )
                decoder_buffer = {}
                return {
                    'register_file': register_file,
                    'decoder_buffer': decoder_buffer,
                    'is_executor_stalled': is_executor_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, register_file [instr.rt]]
                    }

            # Load : rt <- mem [imm (rs)]
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'L'):
                memaddr = (decoder_buffer ['rs'] [1]
                           +
                           decoder_buffer ['immediate'])
                decoder_buffer = {}
                return {
                    'register_file': register_file,
                    'decoder_buffer': decoder_buffer,
                    'is_executor_stalled': is_executor_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': instr.rt,
                    'memaddr': memaddr
                    }

            # Store: mem [imm (rs)] <- rt
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'S'):
                memaddr = (decoder_buffer ['rs'] [1]
                           +
                           decoder_buffer ['immediate'])
                decoder_buffer = {}
                return {
                    'register_file': register_file,
                    'decoder_buffer': decoder_buffer,
                    'is_executor_stalled': is_executor_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, register_file [instr.rt]],
                    'memaddr': memaddr,
                    }

        else:
            is_executor_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                }

        # BEQ and BNE
        if (decoder_buffer.has_key ('rs') and
            decoder_buffer.has_key ('immediate') and
            decoder_buffer.has_key ('rt')):
            condition_output = True
            if (len (instr.opcode) == 3 and
                instr.opcode == 'BEQ'):
                condition_output = (
                    decoder_buffer ['rs'] [1]
                    ==
                    decoder_buffer ['rt'] [1]
                )
            elif (len (instr.opcode) == 3 and
                instr.opcode == 'BNE'):
                condition_output = not (
                    decoder_buffer ['rs'] [1]
                    ==
                    decoder_buffer ['rt'] [1]
                )
            decoder_buffer = {}
            if condition_output:
                PC = npc + 4 * instr.immediate
                print 'BNE/BEQ: PC changed to', PC
            else:
                # TODO
                PC = npc

            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                'instr': instr,
                'npc': npc,
                'PC': PC,
                }
        else: 
            # TODO: Should this be set to True here?
            # is_executor_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                }

    def execute (self, decoder_buffer):
        """
        """
        if decoder_buffer.get('is_mem_stalled', False): 
            return {}
        if not decoder_buffer.has_key ('instr'): 
            return {}

        instr = decoder_buffer ['instr']
        executor_stalled = False

        if instr.type == 'J':
            return decoder_buffer
        if instr.type == 'R':
            return execute_R_instruction(decoder_buffer)
        if instr.type == 'I':
            return execute_I_instruction(decoder_buffer)

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

            # TODO: WHOA!!! register_file shouldn't be accessed in
            # this stage.
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
    
    # TODO
    def get_stage_output(self, memory, register_file, pc, instr_count, 
                         stage_name):
        """Return the output buffer of stage given the initial conditions.
        
        All the stages before stage_name will be executed.
        
        Arguments:
        - `memory`:
        - `register_file`:
        - `pc`:
        - `stage_name`:
        """
        fetch_input_buffer = {
            'memory': memory,
            'PC': pc,
            'instr_count': instr_count,
            }
        
        fetcher_buffer = self.fetch_instruction(fetch_input_buffer)

        if stage_name == 'fetch':
            return fetcher_buffer

        fetcher_buffer.update({
            'register_file': register_file
            })
        decoder_buffer = self.decode_instruction(fetcher_buffer)

        if stage_name == 'decode':
            return decoder_buffer

        mem_buffer = self.execute(decoder_buffer)
        if stage_name == 'execute':
            return mem_buffer


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
            self.decoder_buffer = self.decode_instruction () or self.decoder_buffer

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
