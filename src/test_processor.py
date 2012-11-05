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
        instruction_list = [
            'I ADDI R1 R1 1',
            'I ADDI R2 R2 2',
            'I ADDI R5 R5 89',
            'I BEQ  R2 R5 4',
            'R ADD  R1 R2 R3',
            'R ADD  R2 R0 R1',
            'R ADD  R3 R0 R2',
            'J J    3',
            'I ADDI R9 R9 999',
            ]
        instruction_list = [instruction_string.split()
                            for instruction_string in instruction_list]
        self.memory = Memory.Memory(instruction_list)
        self.register_file = RegisterFile()
        self.processor = Processor.Processor(self.memory, 0)

    def test_execute_one_cycle(self): 
        self.processor.execute_one_cycle()
        print self.register_file
        self.processor.print_buffers()

    def test_are_instructions_in_flight(self): 
        self.assertFalse(self.processor.are_instructions_in_flight())
        self.processor.execute_one_cycle()
        self.assertTrue(self.processor.are_instructions_in_flight())

    def test_execute_cycles(self): 
        self.processor.execute_cycles(1)
        print self.register_file
        self.processor.print_buffers()

    def tearDown(self):
        pass

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
