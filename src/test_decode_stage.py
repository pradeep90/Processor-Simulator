#!/usr/bin/python

import decode_stage
import Processor
import Memory
import Instruction
import unittest
from RegisterFile import RegisterFile
from pprint import pprint
from fetcher_buffer import FetcherBuffer
from fetch_input_buffer import FetchInputBuffer
from decoder_buffer import DecoderBuffer

class DecodeStageTest(unittest.TestCase):
    def setUp(self):
        self.register_file = RegisterFile()
    
    def tearDown(self):
        pass

    def set_up_decode_stage(self, instruction_string):
        """Set up Decode Stage with the appropriate fetcher_buffer, etc.
        
        Arguments:
        - `instruction_string`:
        """
        self.instruction_string = instruction_string
        self.instr = Instruction.Instruction (self.instruction_string.strip().split())
        self.memory = Memory.Memory([self.instruction_string.strip().split()])
        self.fetcher_buffer = Processor.Processor.get_stage_output(
            self.memory, self.register_file, 0, 0, 'fetch')
        self.decoder_buffer = DecoderBuffer()
        self.decode_stage = decode_stage.DecodeStage(self.fetcher_buffer,
                                                     self.decoder_buffer,
                                                     self.register_file)

    def test_decode_R_instruction(self):
        self.set_up_decode_stage('R ADD  R1 R2 R3')
        self.register_file.setClean(self.instr.rs)
        self.register_file.setClean(self.instr.rt)

        decoder_buffer = DecoderBuffer({
            'instr': self.instr,
            'rs': [self.instr.rs, self.register_file[self.instr.rs]],
            'rt': [self.instr.rt, self.register_file[self.instr.rt]],
            'npc': self.fetcher_buffer.npc,
            })
        self.decode_stage.decode_R_instruction()

        self.assertFalse(self.decode_stage.is_stalled)
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertTrue(self.decode_stage.register_file.isDirty(self.instr.rd))
        self.assertEqual(self.decode_stage.fetcher_buffer, FetcherBuffer())

    def test_decode_R_instruction_dirty_reg(self): 
        self.set_up_decode_stage('R ADD  R1 R2 R3')
        self.register_file.setDirty(self.instr.rt)
        decoder_buffer = DecoderBuffer()
        self.decode_stage.decode_R_instruction()

        self.assertTrue(self.decode_stage.is_stalled)
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertTrue(self.decode_stage.register_file.isDirty(self.instr.rd))
        self.assertEqual(self.decode_stage.fetcher_buffer, self.fetcher_buffer)

    def test_decode_I_instruction_funct_and_load(self):
        self.set_up_decode_stage('I ADDI R1 R1 1')
        is_decoder_stalled = False
        self.register_file.setClean(self.instr.rs)
    
        decoder_buffer = DecoderBuffer({
            'instr': self.instr,
            'rs': [self.instr.rs, self.register_file [self.instr.rs]],
            'npc': self.fetcher_buffer.npc,
            'immediate': self.instr.immediate,
            })
        self.decode_stage.decode_I_instruction()

        self.assertFalse(self.decode_stage.is_stalled)
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertTrue(self.register_file.isDirty(self.instr.rt))
        self.assertEqual(self.decode_stage.fetcher_buffer, FetcherBuffer())

    def test_decode_I_instruction_funct_and_load_dirty_reg(self): 
        self.set_up_decode_stage('I ADDI R1 R1 1')
        self.register_file.setDirty(self.instr.rs)
        decoder_buffer = DecoderBuffer()
        self.decode_stage.decode_I_instruction()

        self.assertTrue(self.decode_stage.is_stalled)
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertTrue(self.register_file.isDirty(self.instr.rt))
        self.assertEqual(self.decode_stage.fetcher_buffer, self.fetcher_buffer)

    def test_decode_I_instruction_store_and_branch(self):
        self.set_up_decode_stage('I BEQ  R2 R5 4')
        is_decoder_stalled = False

        self.register_file.setClean(self.instr.rs)
        self.register_file.setClean(self.instr.rt)

        decoder_buffer = DecoderBuffer({
            'instr': self.instr,
            'rs': [self.instr.rs, self.register_file [self.instr.rs]],
            'rt': [self.instr.rt, self.register_file [self.instr.rt]],
            'npc': self.fetcher_buffer.npc,
            'immediate': self.instr.immediate,
            })
        self.decode_stage.decode_I_instruction()

        self.assertFalse(self.decode_stage.is_stalled)
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertEqual(self.decode_stage.fetcher_buffer, FetcherBuffer())

    def test_decode_I_instruction_store_and_branch_dirty_reg(self): 
        self.set_up_decode_stage('I BEQ  R2 R5 4')
        is_decoder_stalled = False
        self.register_file.setDirty(self.instr.rs)
        decoder_buffer = DecoderBuffer()

        self.decode_stage.decode_I_instruction()
        self.assertTrue(self.decode_stage.is_stalled)
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertEqual(self.decode_stage.fetcher_buffer, self.fetcher_buffer)

    def test_get_jump_address(self): 
        instruction_string = 'J J    3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        npc = 4
        self.assertEqual(decode_stage.DecodeStage.get_jump_address(npc, instr), 12)

    def test_decode_J_instruction(self):
        self.set_up_decode_stage('J J    3')
        is_decoder_stalled = False

        decoder_buffer = DecoderBuffer({
            'instr': self.instr,
            'npc': self.fetcher_buffer.npc,
            'PC': 12,
            })
        self.decode_stage.decode_J_instruction()
        self.assertEqual(self.decode_stage.decoder_buffer,
                         decoder_buffer)
        self.assertEqual(self.decode_stage.fetcher_buffer, FetcherBuffer())

    def test_decodeInstruction(self): 
        self.set_up_decode_stage('R ADD  R1 R2 R3')
        self.decode_stage.decode_instruction(True)
        self.assertEqual(
            self.decode_stage.decoder_buffer, 
            DecoderBuffer())

        self.fetcher_buffer.instr = None
        self.decode_stage.decode_instruction()
        self.assertEqual(
            self.decode_stage.decoder_buffer, 
            DecoderBuffer())

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DecodeStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
