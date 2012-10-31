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
        self.fetch_input_buffer = FetchInputBuffer({
            'PC': 0,
            'instr_count': 0,
            })
        self.fetcher_buffer = FetcherBuffer({})
        self.fetch_stage = fetch_stage.FetchStage(self.memory, 
                                                  self.fetch_input_buffer, 
                                                  self.fetcher_buffer)
    
    def tearDown(self):
        pass
    
    def test_fetch_instruction_decoder_stall(self):
        self.fetch_stage.fetch_instruction(True)
        self.assertEqual(self.fetch_stage.fetcher_buffer,
                         FetcherBuffer({}))

    def test_fetch_instruction_normal(self): 
        ans_fetcher_buffer = FetcherBuffer({
            'PC': 0,
            'instr': Instruction.Instruction (self.memory[0]),
            'npc': 4
            })
        self.fetch_stage.fetch_instruction()
        self.assertEqual(self.fetch_stage.fetcher_buffer, ans_fetcher_buffer)

    def test_fetch_instruction_out_of_bound_pc(self): 
        self.fetch_input_buffer['PC'] = 200000
        self.fetch_stage.fetch_instruction(self.fetch_input_buffer)
        self.assertEqual(self.fetch_stage.fetcher_buffer,
                         FetcherBuffer())
	
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FetchStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
