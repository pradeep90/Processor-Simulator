import sys
import time
from collections import defaultdict

from reg_file import RegFile
from exe_module import ExeModule
from pprint import pprint
from fetch_stage import FetchStage
from decode_stage import DecodeStage
from operations import *

class Processor(object):
    """Superscalar MIPS Processor containing all the stages."""

    def __init__(self, hex_code_file, initial_state_file):
        """Initialize Processor with program and memory and reg state.

        Create RegisterFiles.
        Create the stages - Fetch, Decode, and Execution.
        """ 
        self.npc_line = [0]
        self.controller = dict()
        self.Memory = defaultdict(lambda:0)
        instruction_cache = hex_code_file.readlines()
        self.instr_queue = []
        
        self.FPRegisterFile = [{'Value': i+1,
                                'Busy': False,
                                'ROB_index': 0} for i in xrange(10)]
        
        self.IntRegisterFile = [{'Value': i,
                                 'Busy': False,
                                 'ROB_index': 0} for i in xrange(32)]
        
        self.set_initial_state(initial_state_file)

        self.fetch_buffer = dict()
        self.fetch_buffer['IR'] = ''

        self.fetch_stage = FetchStage(0, self.npc_line, 
                                      self.fetch_buffer, 
                                      instruction_cache)

        self.decode_stage = DecodeStage(self.fetch_buffer)

        self.executor = ExeModule(self.FPRegisterFile, self.IntRegisterFile,
                                  self.controller, self.instr_queue,
                                  self.Memory, self.npc_line)
        
        self.modules = [self.executor,]

        self.num_of_instructions = 0
        self.num_of_cycles = 0

    def run(self):
        """Keep triggering each of the stages.

        Stop when there are no more instructions or there is an error.
        Print state of the Processor at the end.
        """ 
        while True:
            if len(self.instr_queue) <= ROB_MAX_SIZE:
                ret_val = self.fetch_stage.trigger_clock()
                if ret_val == -77:
                    self.print_final_output()

                # TODO: change this to trigger_clock
                self.decode_stage._decode_instr()
                self.print_curr_instr()
                self.instr_queue.append(self.decode_stage.current_instr)
            else:
                # TODO:  
                print "Do something for this!"
                sys.exit(1)

            for module in self.modules:
                ret_val = module.trigger_clock()

    # TODO: Make the inputs be Python code.
    def set_initial_state(self, initial_state_file):
        """Get the initial state of registers and Memory from initial_state_file.

        Print the initial values.
        """ 
        setting_reg = True
        for line in initial_state_file.readlines():
            split_line = line.split()
            try:
                int(split_line[0])
            except:
                setting_reg = False
                continue
            if setting_reg:
                self.IntRegisterFile[int(split_line[0])]['Value'] = int(split_line[1])
            else:
                self.Memory[int(split_line[0])] = int(split_line[1])
        
        for reg in self.IntRegisterFile:
            print reg

        for mem in self.Memory:
            print mem, self.Memory[mem]

        print

    def print_final_output(self, ):
        """Print the final output.
        """
        print 'Bye bye'
        print 'self.FPRegisterFile: '
        pprint(self.FPRegisterFile)
        print 'self.IntRegisterFile: '
        pprint(self.IntRegisterFile)
        print 'Memory'
        pprint(dict(self.Memory))
        sys.exit(0)
        

    def print_curr_instr(self, ):
        """Print the current instruction.
        """
        print "-" * 20, self.decode_stage.current_instr, "-" * 20

