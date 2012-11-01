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
from executer_buffer import ExecuterBuffer

class ExecuteStageTest(unittest.TestCase):
    def setUp(self):
        self.register_file = RegisterFile()
    
    def tearDown(self):
        pass

    def set_up_execute_stage(self, instruction_string):
        """Set up Execute Stage with the appropriate decoder_buffer, etc.
        
        Arguments:
        - `instruction_string`:
        """
        self.instruction_string = instruction_string
        self.instr = Instruction.Instruction (self.instruction_string.strip().split())
        self.memory = Memory.Memory([self.instruction_string.strip().split()])
        self.decoder_buffer = Processor.Processor.get_stage_output(
            self.memory, self.register_file, 0, 0, 'decode')
        self.executer_buffer = ExecuterBuffer()
        self.execute_stage = execute_stage.ExecuteStage(self.decoder_buffer,
                                                        self.executer_buffer,
                                                        self.register_file)
    
    # def test_execute_R_instruction(self): 
    #     self.set_up_execute_stage('R ADD  R1 R2 R3')

    #     self.execute_stage.execute(True)

    #     executer_buffer = ExecuterBuffer({
    #         'is_executer_stalled': False,
    #         'instr': self.instr,
    #         'npc': self.decoder_buffer.npc,
    #         'rd': [self.instr.rd, self.register_file [self.instr.rd]],
    #         })
    #     self.execute_stage.execute_R_instruction()
    #     self.assertEqual(self.execute_stage.executer_buffer, 
    #                      mem_buffer,
    #                      "operands in buffer")

    #     decoder_buffer.pop('rs')
    #     mem_buffer = {
    #         'is_executer_stalled': True,
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
        #         'is_executer_stalled': False,
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

    def test_execute(self): 
        self.set_up_execute_stage('R ADD  R1 R2 R3')

        self.execute_stage.execute(True)
        self.assertEqual(self.execute_stage.executer_buffer, 
                         ExecuterBuffer())

        self.decoder_buffer.instr = None
        self.execute_stage.execute(True)
        self.assertEqual(self.execute_stage.executer_buffer, 
                         ExecuterBuffer())
	
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ExecuteStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
