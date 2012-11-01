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
from decoder_buffer import DecoderBuffer

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
    
    def test_execute_R_instruction(self): 
        self.register_file[1] = 3
        self.register_file[2] = 7
        self.set_up_execute_stage('R ADD  R1 R2 R3')

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': False,
            'instr': self.instr,
            'npc': self.decoder_buffer.npc,
            'rd': [self.instr.rd, self.register_file[1] + self.register_file[2]],
            })

        self.execute_stage.execute_R_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         DecoderBuffer())

    def test_execute_R_instruction_no_operands(self): 
        self.register_file[1] = 3
        self.register_file[2] = 7
        self.set_up_execute_stage('R ADD  R1 R2 R3')
        self.decoder_buffer.rs = None

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': True,
            })

        self.execute_stage.execute_R_instruction()
        self.assertEqual(self.execute_stage.executer_buffer,
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, self.decoder_buffer)

    def test_execute_I_instruction_ADDI_etc_no_operands(self): 
        self.set_up_execute_stage('R ADD  R1 R2 R3')
        self.decoder_buffer.rs = None

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': True,
            })

        self.execute_stage.execute_R_instruction()
        self.assertEqual(self.execute_stage.executer_buffer,
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, self.decoder_buffer)

    def test_execute_I_instruction_ADDI(self): 
        self.register_file[1] = 3
        self.set_up_execute_stage('I ADDI R1 R1 1')

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': False,
            'instr': self.instr,
            'npc': self.decoder_buffer.npc,
            'rt': [self.instr.rt, self.register_file[1] + 1],
            })

        self.execute_stage.execute_I_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         DecoderBuffer())

    def test_execute_I_instruction_LW(self): 
        self.register_file[2] = 8
        self.set_up_execute_stage('I LW  R2 R5 4')

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': False,
            'instr': self.instr,
            'npc': self.decoder_buffer.npc,
            'rt': self.instr.rt,
            'memaddr': 12,
            })

        self.execute_stage.execute_I_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         DecoderBuffer())

    def test_execute_I_instruction_STORE(self): 
        self.register_file[2] = 8
        self.set_up_execute_stage('I SW  R2 R5 4')

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': False,
            'instr': self.instr,
            'npc': self.decoder_buffer.npc,
            'rt': [self.instr.rt, self.register_file [self.instr.rt]],
            'memaddr': 12,
            })

        self.execute_stage.execute_I_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         DecoderBuffer())

    def test_execute_I_instruction_BEQ_missing_operands(self): 
        self.register_file[2] = 8
        self.set_up_execute_stage('I BEQ  R2 R5 4')

        self.decoder_buffer.rs = None
        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': True,
            })

        self.execute_stage.execute_I_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         self.decoder_buffer)

    def test_execute_I_instruction_BEQ_true(self): 
        self.register_file[2] = 8
        self.register_file[5] = 8
        self.set_up_execute_stage('I BEQ  R2 R5 4')

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': False,
            'instr': self.instr,
            'npc': self.decoder_buffer.npc,
            'PC': self.decoder_buffer.npc + 4 * 4,
            })

        self.execute_stage.execute_I_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         DecoderBuffer())

    def test_execute_I_instruction_BEQ_false(self): 
        self.register_file[2] = 8
        self.register_file[5] = 7
        self.set_up_execute_stage('I BEQ  R2 R5 4')

        executer_buffer = ExecuterBuffer({
            'is_executer_stalled': False,
            'instr': self.instr,
            'npc': self.decoder_buffer.npc,
            'PC': self.decoder_buffer.npc,
            })

        self.execute_stage.execute_I_instruction()
        self.assertEqual(self.execute_stage.executer_buffer, 
                         executer_buffer)
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         DecoderBuffer())

    def test_execute(self): 
        self.set_up_execute_stage('R ADD  R1 R2 R3')

        self.execute_stage.execute(True)
        self.assertEqual(self.execute_stage.executer_buffer, 
                         ExecuterBuffer())

        self.decoder_buffer.instr = None
        self.execute_stage.execute(True)
        self.assertEqual(self.execute_stage.executer_buffer, 
                         ExecuterBuffer())
        self.assertEqual(self.execute_stage.decoder_buffer, 
                         self.decoder_buffer)
	
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ExecuteStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
