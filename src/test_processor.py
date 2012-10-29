#!/usr/bin/python

import Processor
import Memory
import Instruction
import unittest
from RegisterFile import RegisterFile
from pprint import pprint
from fetcher_buffer import FetcherBuffer
from fetch_input_buffer import FetchInputBuffer

class ProcessorTest(unittest.TestCase):
    
    def setUp(self):
        
        hex_instruction_list = [
            '00001020',                   # I instruction
            '00011820',
            '00432020',
            '00A12822',
            '00031025',                   # R instruction
            '00041825',
            'AC860000',
            '20C60001',
            '1005000A',
            '08000002', 
            ]

        # Actual Code:
        # I ADDI R1 R1 1
        # I ADDI R2 R2 2
        # I ADDI R5 R5 89
        # I BEQ  R2 R5 4
        # R ADD  R1 R2 R3
        # R ADD  R2 R0 R1
        # R ADD  R3 R0 R2
        # J J    3
        # I ADDI R9 R9 999
        
        bin_instruction_list = [
            Memory.Memory.get_bin_from_hex_instruction(instruction) 
            for instruction in hex_instruction_list]
        self.memory = Memory.Memory(bin_instruction_list)
        self.register_file = RegisterFile()
        self.processor = Processor.Processor(self.memory, 0)

    def tearDown(self):
        pass

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
