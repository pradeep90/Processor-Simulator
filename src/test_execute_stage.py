#!/usr/bin/python

import execute_stage
import Processor
import Memory
import Instruction
import unittest
from RegisterFile import RegisterFile
from pprint import pprint
from fetcher_buffer import FetcherBuffer
from fetch_input_buffer import FetchInputBuffer

class ExecuteStageTest(unittest.TestCase):
    def setUp(self):
        self.register_file = RegisterFile()
    
    def tearDown(self):
        pass
    
    # def test_execute_R_instruction(self): 
    #     instruction_string = 'R ADD  R1 R2 R3'
    #     instr = Instruction.Instruction (instruction_string.strip().split())
    #     register_file = self.register_file
    #     npc = 4

    #     memory = Memory.Memory([instruction_string.strip().split()])
    #     decoder_buffer = Processor.Processor.get_stage_output(
    #         memory, register_file, 0, 0, 'decode')

    #     mem_buffer = {
    #         'register_file': register_file,
    #         'decoder_buffer': {},
    #         'is_executor_stalled': False,
    #         'instr': instr,
    #         'npc': npc,
    #         'rd': [instr.rd, register_file [instr.rd]],
    #         }
    #     self.assertEqual(
    #         execute_stage.ExecuteStage.execute_R_instruction(decoder_buffer), 
    #         mem_buffer,
    #         "operands in buffer")

    #     decoder_buffer.pop('rs')
    #     mem_buffer = {
    #         'register_file': register_file,
    #         'decoder_buffer': decoder_buffer,
    #         'is_executor_stalled': True,
    #         }
    #     self.assertEqual(
    #         execute_stage.ExecuteStage.execute_R_instruction(decoder_buffer),
    #         mem_buffer,
    #         "stall")

    def test_execute_I_instruction(self): 
        # instruction_list = [
        #     'I ADDI R1 R1 1',
        #     'I LW  R2 R5 4',
        #     'I BEQ  R2 R5 4',
        # ]

        # rt_val_list = [
        #     [1, 1],
        #     5,
        #     None,
        # ]
        # instruction_list = [instruction.strip().split() 
        #                     for instruction in instruction_list]
        # register_file = self.register_file
        # memory = Memory.Memory(instruction_list)
        # npc = 4

        # register_file_list = [RegisterFile()] * len(instruction_list)
        # mem_buffer_list = [
        #     {
        #         'register_file': register_file_list[i],
        #         'decoder_buffer': {},
        #         'is_executor_stalled': False,
        #         'instr': Instruction.Instruction(memory[i * 4]),
        #         'npc': npc + i * 4,
        #         'rt': rt_val_list[i],
        #         'memaddr': 4,
        #     }
        #     for i in xrange(len(instruction_list))]

        # for i in xrange(len(instruction_list)):
        #     decoder_buffer = Processor.Processor.get_stage_output(
        #         memory, register_file_list[i], i * 4, 0, 'decode')
        #     actual_mem_buffer = execute_stage.ExecuteStage.execute_I_instruction(decoder_buffer)
        #     pprint(actual_mem_buffer)
        #     for key in actual_mem_buffer:
        #         print key
        #         self.assertEqual(actual_mem_buffer[key], mem_buffer_list[i][key])
        pass

    # def test_execute(self): 
    #     instruction_string = 'R ADD  R1 R2 R3'
    #     instr = Instruction.Instruction (instruction_string.strip().split())
    #     register_file = self.register_file
    #     npc = 4

    #     decoder_buffer = {
    #         'instr': instr,
    #         'npc': npc,
    #         'register_file': register_file,
    #         'is_mem_stalled': True,
    #     }

    #     self.assertEqual(execute_stage.ExecuteStage.execute(decoder_buffer), {})

    #     decoder_buffer.pop('is_mem_stalled')
    #     decoder_buffer.pop('instr')
    #     self.assertEqual(execute_stage.ExecuteStage.execute(decoder_buffer), {})
	
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ExecuteStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
