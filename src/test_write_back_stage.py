#!/usr/bin/python

from collections import defaultdict
from decoder_buffer import DecoderBuffer
from executer_buffer import ExecuterBuffer
from fetcher_buffer import FetcherBuffer
from fetch_input_buffer import FetchInputBuffer
from memory_buffer import MemoryBuffer
from pprint import pprint
from RegisterFile import RegisterFile
import execute_stage
import Instruction
import Memory
import memory_stage
import Processor
import unittest
import write_back_stage

class WriteBackStageTest(unittest.TestCase):
    def setUp(self):
        self.register_file = RegisterFile()
    
    def tearDown(self):
        pass

    def set_up_write_back_stage(self, instruction_string):
        """Set up WriteBackStage with the appropriate memory_buffer, etc.
        """
        self.instruction_string = instruction_string
        self.instr = Instruction.Instruction (self.instruction_string.strip().split())
        self.memory = Memory.Memory([self.instruction_string.strip().split()])

        self.memory_buffer = Processor.Processor.get_stage_output(
            self.memory, self.register_file, 0, 0, 'memory')

        self.write_back_stage = write_back_stage.WriteBackStage(
            self.memory_buffer,
            self.register_file)

    def test_write_back_no_instr(self): 
        self.set_up_write_back_stage('R ADD  R1 R2 R3')
        self.memory_buffer.instr = None
        self.write_back_stage.write_back()
        self.assertEqual(self.write_back_stage.memory_buffer, 
                         self.memory_buffer)

    def test_write_back_R(self): 
        self.set_up_write_back_stage('R ADD  R1 R2 R3')
        self.write_back_stage.write_back()
        self.assertEqual(self.write_back_stage.memory_buffer, 
                         MemoryBuffer())       
        self.assertEqual(
            self.write_back_stage.register_file[self.instr.rd], 
                self.memory_buffer.rd[1])
        self.assertTrue(self.register_file.isClean(self.instr.rd))

    def test_write_back_I(self): 
        self.set_up_write_back_stage('I LW  R2 R5 4')
        self.write_back_stage.write_back()
        self.assertEqual(self.write_back_stage.memory_buffer, 
                         MemoryBuffer())       
        self.assertTrue(self.register_file.isClean(self.instr.rt))

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(WriteBackStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
