import sys
import time
from collections import defaultdict

from reg_file import RegFile
from instr_unit import InstrUnit
from exe_module import ExeModule
from pprint import pprint

class Processor(object):
    """ The super scalar MIPS Processor which will contain 
        all the modules.
    """
    def __init__(self, hex_code_file, initial_state_file):
        self.npc_line = [0]
        self.controller = dict()
        self.Memory = defaultdict(lambda:0)
        instruction_cache = hex_code_file.readlines()
        self.instr_queue = []

        self.FPRegisterFile = [{'Value': i+1,\
                       'Busy': False,\
                       'ROB_index': 0} for i in xrange(10)]

        self.IntRegisterFile = [{'Value': i,\
                       'Busy': False,\
                       'ROB_index': 0} for i in xrange(32)]

        self.setInitialState(initial_state_file)

        self.instruction_fetcher = InstrUnit(0, instruction_cache,\
                                            self.controller,\
                                            self.instr_queue,\
                                            self.npc_line,
                                            self.IntRegisterFile,
                                            self.FPRegisterFile)

        self.executor = ExeModule(self.FPRegisterFile, self.IntRegisterFile,\
                                  self.controller, self.instr_queue,\
                                  self.Memory, self.npc_line)

        self.modules = [self.executor,\
                        self.instruction_fetcher]

        self.num_of_instructions = 0
        self.num_of_cycles = 0

    def run(self):
        while True:
            for module in self.modules:
                ret_val = module.trigger_clock()
                if ret_val == -77:
                    print 'Memory'
                    pprint(dict(self.Memory))
                    sys.exit(1)

    def setInitialState(self, initial_state_file):
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

