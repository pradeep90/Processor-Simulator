#!/usr/bin/python

from collections import defaultdict
from decoder_buffer import DecoderBuffer
from executer_buffer import ExecuterBuffer
from fetcher_buffer import FetcherBuffer
from memory_buffer import MemoryBuffer
from fetch_input_buffer import FetchInputBuffer
from pprint import pprint
from RegisterFile import RegisterFile
import execute_stage
import Instruction
import Memory
import memory_stage
import Processor
import unittest

class MemoryStageTest(unittest.TestCase):
    def setUp(self):
        # This is used only for passing into the stages before memory
        # so that we can get executer_buffer.
        self.register_file = RegisterFile()

        self.data_memory_key_fn = lambda: -1
        self.data_memory = defaultdict (self.data_memory_key_fn)
    
    def tearDown(self):
        pass

    def set_up_memory_stage(self, instruction_string):
        """Set up Memory Stage with the appropriate executer_buffer, etc.
        
        Arguments:
        - `instruction_string`:
        """
        self.instruction_string = instruction_string
        self.instr = Instruction.Instruction (self.instruction_string.strip().split())
        self.memory = Memory.Memory([self.instruction_string.strip().split()])
        self.executer_buffer = Processor.Processor.get_stage_output(
            self.memory, self.register_file, 0, 0, 'execute')
        self.memory_buffer = MemoryBuffer()
        self.memory_stage = memory_stage.MemoryStage(self.executer_buffer,
                                                     self.memory_buffer,
                                                     self.data_memory)

    def test_do_memory_operation_stall(self): 
        self.set_up_memory_stage('I LW  R2 R5 4')

        self.memory_stage.do_memory_operation(True)
        self.assertEqual(self.memory_stage.memory_buffer, 
                         MemoryBuffer())

        self.executer_buffer.instr = None
        self.memory_stage.do_memory_operation(True)
        self.assertEqual(self.memory_stage.memory_buffer, 
                         MemoryBuffer())
        self.assertEqual(self.memory_stage.executer_buffer, 
                         self.executer_buffer)

    def test_do_memory_operation_load(self): 
        self.register_file[2] = 8
        self.data_memory[8 + 4] = 174
        self.set_up_memory_stage('I LW  R2 R5 4')

        memory_buffer = MemoryBuffer({
            'is_memory_stalled': False,
            'instr': self.instr,
            'rt': [self.instr.rt, 174],
            })

        self.memory_stage.do_memory_operation()
        self.assertEqual(self.memory_stage.memory_buffer, 
                         memory_buffer)
        self.assertEqual(self.memory_stage.executer_buffer, 
                         ExecuterBuffer())

    def test_do_memory_operation_store(self): 
        self.register_file[2] = 8
        self.register_file[5] = 174
        self.set_up_memory_stage('I SW  R2 R5 4')

        memory_buffer = MemoryBuffer({
            'is_memory_stalled': False,
            'instr': self.instr,
            })

        self.memory_stage.do_memory_operation()
        self.assertEqual(self.memory_stage.memory_buffer, 
                         memory_buffer)
        self.assertEqual(self.memory_stage.executer_buffer, 
                         ExecuterBuffer())
        self.assertEqual(self.data_memory[12], 174)

    # TODO:
    # def test_do_memory_operation_stall(self): 
    #     self.set_up_memory_stage('I LW R2 R5 4')

    #     memory_buffer = MemoryBuffer({
    #         'is_memory_stalled': True,
    #         })

    #     self.memory_stage.do_memory_operation()
    #     self.assertEqual(self.memory_stage.memory_buffer, 
    #                      memory_buffer)
    #     self.assertEqual(self.memory_stage.executer_buffer, 
    #                      self.executer_buffer)
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(MemoryStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
