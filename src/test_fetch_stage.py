#!/usr/bin/python

import fetch_stage
from fetch_input_buffer import FetchInputBuffer
from fetcher_buffer import FetcherBuffer
import Instruction
import Memory
import unittest

class FetchStageTest(unittest.TestCase):
    def setUp(self):
        self.instruction_string = 'R ADD  R1 R2 R3'
        self.instr = Instruction.Instruction (self.instruction_string.strip().split())
        self.memory = Memory.Memory([self.instruction_string.strip().split()])
        self.fetch_stage = fetch_stage.FetchStage()
    
    def tearDown(self):
        pass
    
    def test_fetch_instruction(self):
        # Decoder Stalled
        fetch_input_buffer = FetchInputBuffer({
            'memory': self.memory,
            'PC': 0,
            'instr_count': 0,
            })
        self.assertEqual(self.fetch_stage.fetch_instruction(fetch_input_buffer, 
                                                          True),
                         FetcherBuffer({}))

        fetcher_buffer = {'instr' : Instruction.Instruction (self.memory[0]),
                          'npc' : 4}
        actual_buffer = self.fetch_stage.fetch_instruction(fetch_input_buffer)
        for key in fetcher_buffer.keys():
            self.assertEqual(actual_buffer[key],
                             fetcher_buffer[key])

        fetch_input_buffer['PC'] = 200000
        self.assertEqual(self.fetch_stage.fetch_instruction(fetch_input_buffer),
                         {})
	
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FetchStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
