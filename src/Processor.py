#!/usr/bin/env python

from collections import defaultdict
import sys
from warnings import warn
from Instruction import Instruction
from Memory import Memory
from RegisterFile import RegisterFile
from pprint import pprint
from fetcher_buffer import FetcherBuffer
from decoder_buffer import DecoderBuffer
from fetch_stage import FetchStage
from decode_stage import DecodeStage
from execute_stage import ExecuteStage
import pickle

default_data_file_name =  'new-cycle-data.pickle'

class Processor (object):
    fetcher_buffer = FetcherBuffer()
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
    
    # TODO: Be careful. In reality, the stages are executed in reverse
    # order.
    @staticmethod
    def get_stage_output(memory, register_file, pc, instr_count, 
                         stage_name):
        """Return the output buffer of stage given the initial conditions.
        
        All the stages before stage_name will be executed.
        
        Arguments:
        - `memory`:
        - `register_file`:
        - `pc`:
        - `stage_name`:

        TODO: Maybe just take the stages as input later.
        """
        fetch_input_buffer = {
            'PC': pc,
            'instr_count': instr_count,
            }

        fetch_stage = FetchStage(memory)
        fetcher_buffer = fetch_stage.fetch_instruction(fetch_input_buffer)

        if stage_name == 'fetch':
            return fetcher_buffer

        fetcher_buffer.register_file = register_file

        decode_stage = DecodeStage(fetcher_buffer, DecoderBuffer(), register_file)
        decoder_buffer = decode_stage.decode_instruction(fetcher_buffer)

        if stage_name == 'decode':
            return decoder_buffer

        mem_buffer = ExecuteStage.execute(decoder_buffer)
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
