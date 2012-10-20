#!/usr/bin/python

import Processor
import Memory
import Instruction
import unittest
from pprint import pprint

class ProcessorTest(unittest.TestCase):
    
    def setUp(self):
        
        hex_instruction_list = [
            '00001020',
            '00011820',
            '00432020',
            '00A12822',
            '00031025',
            '00041825',
            'AC860000',
            '20C60001',
            '1005000A',
            '08000002', 
            ]
        
        bin_instruction_list = [
            Memory.Memory.get_bin_from_hex_instruction(instruction) 
            for instruction in hex_instruction_list]
        self.memory = Memory.Memory(bin_instruction_list)
        self.processor = Processor.Processor(self.memory, 0)

    def tearDown(self):
        pass

    def test_fetch_instruction(self):
        fetch_input_buffer = {'is_decoder_stalled': True}
        self.assertEqual(self.processor.fetch_instruction(fetch_input_buffer),
                         {})

        fetch_input_buffer = {'memory': self.memory,
                              'PC': 0}
        fetcher_buffer = {'instr' : Instruction.Instruction (self.memory[0]),
                          'npc' : 4}
        actual_buffer = self.processor.fetch_instruction(fetch_input_buffer)
        for key in fetcher_buffer.keys():
            self.assertEqual(actual_buffer[key],
                             fetcher_buffer[key])

        fetch_input_buffer['PC'] = 200000
        self.assertEqual(self.processor.fetch_instruction(fetch_input_buffer),
                         {})

    def test_decode_R_instruction(self):
        pass
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
