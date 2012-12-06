import sys
import time
from collections import defaultdict
from commit_stage import CommitStage
from decode_stage import DecodeStage
from execute_module import ExecuteModule
from execute_stage import ExecuteStage
from fetch_stage import FetchStage
from func_unit import *
from issue_stage import IssueStage
from load_store_unit import *
from operations import *
from pprint import pprint
from reg_file import RegFile
from rob import ROB
from write_stage import WriteStage

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

        self.CDB = []
        self.ROB = ROB(ROB_MAX_SIZE, self.CDB, self.IntRegisterFile, self.Memory, self)

        self.execute_module = ExecuteModule(self.Memory, self.CDB, self.ROB)

        self.fetch_buffer = dict()
        self.fetch_buffer['IR'] = ''

        self.fetch_stage = FetchStage(0, self.npc_line, 
                                      self.fetch_buffer, 
                                      instruction_cache)

        self.decode_stage = DecodeStage(self.fetch_buffer)
        
        self.issue_stage = IssueStage(self.ROB, self.instr_queue,
                                      self.IntRegisterFile, self.FPRegisterFile, 
                                      self.execute_module)
        self.write_stage = WriteStage(self.execute_module)
        self.commit_stage = CommitStage(self.ROB)
        self.execute_stage = ExecuteStage(self.execute_module, self.CDB, self.ROB)
        
        self.modules = [self.issue_stage, self.execute_stage, 
                        self.write_stage, self.commit_stage]

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

                self.decode_stage.trigger_clock()
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

    def reset_func_units_and_pc(self, npc):
        """Reset all the FuncUnits and the PC.""" 
        self.npc_line[0] = npc

        self.execute_module.FP_ADD = FuncUnit(2, self.CDB, 3)
        self.execute_module.FP_MUL = FuncUnit(3, self.CDB, 2)
        self.execute_module.BranchFU = FuncUnit(1, self.CDB, 3)
        self.execute_module.Int_Calc = FuncUnit(1, self.CDB, 5)
        self.execute_module.LoadStore = LoadStoreUnit(self.Memory, self.CDB, self.ROB, 4)
        self.execute_module.load_step_1_done = False
