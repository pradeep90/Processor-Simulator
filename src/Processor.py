#!/usr/bin/env python

from collections import defaultdict
from decoder_buffer import DecoderBuffer
from decode_stage import DecodeStage
from executer_buffer import ExecuterBuffer
from execute_stage import ExecuteStage
from fetcher_buffer import FetcherBuffer
from fetch_input_buffer import FetchInputBuffer
from fetch_stage import FetchStage
from Instruction import Instruction
from memory_buffer import MemoryBuffer
from Memory import Memory
from memory_stage import MemoryStage
from write_back_stage import WriteBackStage
from pprint import pprint
from RegisterFile import RegisterFile
from warnings import warn
import pickle
import sys

default_data_file_name =  'new-cycle-data.pickle'

class Processor (object):

    def __init__ (self, memory, start_address):
        self.memory = memory
        self.start_address = start_address
        self.register_file = RegisterFile ()
        self.data_memory_key_fn = lambda: -1
        self.data_memory = defaultdict (self.data_memory_key_fn)

        self.cycle_count = 0
        self.instr_count = 0
        self.PC = 0

        self.fetch_input_buffer = FetchInputBuffer({
            'PC': self.start_address,
            'instr_count': self.instr_count,
            })
        self.fetcher_buffer = FetcherBuffer({})
        self.fetch_stage = FetchStage(self.memory, 
                                      self.fetch_input_buffer, 
                                      self.fetcher_buffer)
        
        self.decoder_buffer = DecoderBuffer()
        self.decode_stage = DecodeStage(self.fetcher_buffer,
                                        self.decoder_buffer,
                                        self.register_file)
        
        self.executer_buffer = ExecuterBuffer()
        self.execute_stage = ExecuteStage(self.decoder_buffer,
                                          self.executer_buffer)
        self.memory_buffer = MemoryBuffer()
        self.memory_stage = MemoryStage(self.executer_buffer,
                                        self.memory_buffer,
                                        self.data_memory)
        self.write_back_stage = WriteBackStage(
            self.memory_buffer,
            self.register_file)

    def print_buffers (self):
        print "PC:", self.fetch_stage.fetch_input_buffer

        print 'fetch_stage.fetch_input_buffer:'
        print self.fetch_stage.fetch_input_buffer
        print 'fetch_stage.fetcher_buffer:'
        print self.fetch_stage.fetcher_buffer
        print
        print 'decode_stage.fetcher_buffer:'
        print self.decode_stage.fetcher_buffer
        print 'decode_stage.decoder_buffer:'
        print self.decode_stage.decoder_buffer
        print
        print 'execute_stage.decoder_buffer:'
        print self.execute_stage.decoder_buffer
        print 'execute_stage.executer_buffer:'
        print self.execute_stage.executer_buffer
        print
        print 'memory_stage.executer_buffer:'
        print self.memory_stage.executer_buffer
        print 'memory_stage.memory_buffer:'
        print self.memory_stage.memory_buffer
        print
        print 'write_back_stage.memory_buffer:'
        print self.write_back_stage.memory_buffer


    # def get_all_curr_data(self):
    #     """Return dict of all data in the Processor at the moment.
    #     """

    #     # TODO: It gives 'Can't pickle instancemethod object' error
    #     # when I have self.data_memory too.

    #     curr_data_dict = {
    #         'fetcher_buffer': self.fetcher_buffer,
    #         'decoder_buffer': self.decoder_buffer,
    #         'executer_buffer': self.executer_buffer,
    #         'memory_buffer': self.memory_buffer,
    #         'decoder_stalled': self.decoder_stalled,
    #         'executer_stalled': self.executer_stalled,
    #         'mem_stalled': self.mem_stalled,
    #         'reg_writer_stalled': self.reg_writer_stalled,
    #         'memory': self.memory,
    #         'start_address': self.start_address,
    #         'register_file': self.register_file,
    #         'PC': self.PC,
    #         'IR': self.IR,
    #         'NPC': self.NPC,
    #         'cycle_count': self.cycle_count,
    #         'instr_count': self.instr_count,
    #         }
    #     return curr_data_dict

    # @staticmethod
    # def save_cycle_data(cycle_data_list, cycle_data_file_name = default_data_file_name):
    #     """Pickle and save cycle_data_list.
        
    #     Arguments:
    #     - `cycle_data_list`:
    #     """

    #     with open(cycle_data_file_name, 'w') as f:
    #         pickle.dump(cycle_data_list, f)

    #     print 'Wrote cycle_data_list to {0}'.format(cycle_data_file_name)

    # @staticmethod
    # def read_saved_data(cycle_data_file_name = default_data_file_name):
    #     """Return cycle data list saved in cycle_data_file_name.
        
    #     Arguments:
    #     - `cycle_data_file_name`:
    #     """
    #     cycle_data_list = []
    #     with open(cycle_data_file_name, 'rb') as f:
    #         cycle_data_list = pickle.load(f)
    #         print 'Read cycle_data_list from {0}'.format(cycle_data_file_name)
    #     return cycle_data_list
    
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
        fetch_input_buffer = FetchInputBuffer({
            'PC': pc,
            'instr_count': instr_count,
            })
        fetcher_buffer = FetcherBuffer()
        fetch_stage = FetchStage(memory, fetch_input_buffer, fetcher_buffer)
        fetch_stage.fetch_instruction()

        if stage_name == 'fetch':
            return fetch_stage.fetcher_buffer

        decode_stage = DecodeStage(fetch_stage.fetcher_buffer, 
                                   DecoderBuffer(), 
                                   register_file)
        decode_stage.decode_instruction()

        if stage_name == 'decode':
            return decode_stage.decoder_buffer

        execute_stage = ExecuteStage(decode_stage.decoder_buffer,
                                     ExecuterBuffer())
        execute_stage.execute()
        if stage_name == 'execute':
            return execute_stage.executer_buffer

        data_memory_key_fn = lambda: -1
        data_memory = defaultdict (data_memory_key_fn)

        memory_stage = MemoryStage(execute_stage.executer_buffer,
                                   MemoryBuffer(),
                                   data_memory)
        memory_stage.do_memory_operation()

        if stage_name == 'memory':
            return memory_stage.memory_buffer

    def are_instructions_in_flight(self, ):
        """Return True iff there exist instructions in-flight.
        """
        return any(not buff.is_empty() for buff in (self.memory_stage.memory_buffer,
                                                    self.execute_stage.executer_buffer,
                                                    self.decode_stage.decoder_buffer,
                                                    self.fetch_stage.fetcher_buffer))
        
    def execute_one_cycle(self, ):
        """Execute one cycle of the Processor.
        """
        self.write_back_stage.write_back()
        self.memory_stage.do_memory_operation()
        self.execute_stage.execute()
        self.decode_stage.decode_instruction()
        self.fetch_stage.fetch_instruction()

        self.write_back_stage.memory_buffer = self.memory_stage.memory_buffer
        self.memory_stage.executer_buffer = self.execute_stage.executer_buffer
        self.execute_stage.decoder_buffer = self.decode_stage.decoder_buffer
        self.decode_stage.fetcher_buffer = self.fetch_stage.fetcher_buffer

        # TODO:
        if self.decode_stage.decoder_buffer.PC is not None:
            # Pass on PC value from decoder_buffer to fetcher_buffer in
            # case of a jump.
            self.fetch_stage.fetch_input_buffer.PC = self.decode_stage.decoder_buffer.PC
        
    def execute_cycles(self, num_cycles = None):
        """Execute num_cycles cycles of the Processor (if possible).

        Else, execute till the program terminates.
        """
        cycle_count = 0

        while True:
            self.execute_one_cycle()

            cycle_count += 1
            print 'Beginning of Cycle #' + str(cycle_count)
            print '=' * 12
            self.print_buffers ()
            print self.register_file

            if not self.are_instructions_in_flight() or (
                    num_cycles is not None and cycle_count == num_cycles):
                break

    def start(self, cycle_data_file_name = default_data_file_name):
        """Start execution of instructions from the start_address.
        """
        self.instruction_address = self.start_address
        self.more_instructions_to_fetch = True
        self.execute_cycles()

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
