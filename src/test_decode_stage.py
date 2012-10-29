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

class DecodeStageTest(unittest.TestCase):
    def setUp(self):
        self.register_file = RegisterFile()
    
    def tearDown(self):
        pass

    def test_decode_R_instruction(self):
        instruction_string = 'R ADD  R1 R2 R3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4
        is_decoder_stalled = False

        register_file.setClean(instr.rs)
        register_file.setClean(instr.rt)

        fetcher_buffer = {
            'instr': instr,
            'npc': npc,
            'register_file': register_file,
        }

        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': {},
            'is_decoder_stalled': False,
            'instr': instr,
            'rs': [instr.rs, register_file [instr.rs]],
            'rt': [instr.rt, register_file [instr.rt]],
            'npc': npc,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_R_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rd))

        register_file.setDirty(instr.rt)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_R_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rd))

    def test_decode_I_instruction_funct_and_load(self):
        instruction_string = 'I ADDI R1 R1 1'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4
        is_decoder_stalled = False

        register_file.setClean(instr.rs)

        fetcher_buffer = {
            'instr': instr,
            'npc': npc,
            'register_file': register_file,
        }

        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': {},
            'is_decoder_stalled': False,
            'instr': instr,
            'rs': [instr.rs, register_file [instr.rs]],
            'npc': npc,
            'immediate': instr.immediate,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rt))

        register_file.setDirty(instr.rs)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rt))

    def test_decode_I_instruction_store_and_branch(self):
        instruction_string = 'I BEQ  R2 R5 4'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4
        is_decoder_stalled = False

        register_file.setClean(instr.rs)
        register_file.setClean(instr.rt)

        fetcher_buffer = {
            'instr': instr,
            'npc': npc,
            'register_file': register_file,
        }

        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': {},
            'is_decoder_stalled': False,
            'instr': instr,
            'rs': [instr.rs, register_file [instr.rs]],
            'rt': [instr.rt, register_file [instr.rt]],
            'npc': npc,
            'immediate': instr.immediate,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)

        register_file.setDirty(instr.rs)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)

    def test_get_jump_address(self): 
        instruction_string = 'J J    3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        npc = 4
        self.assertEqual(decode_stage.DecodeStage.get_jump_address(npc, instr), 12)

    def test_decode_J_instruction(self):
        instruction_string = 'J J    3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4
        is_decoder_stalled = False

        fetcher_buffer = {
            'instr': instr,
            'npc': npc,
            'register_file': register_file,
        }

        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': {},
            'is_decoder_stalled': False,
            'instr': instr,
            'npc': npc,
            'PC': 12,
            }
        self.assertEqual(decode_stage.DecodeStage.decode_J_instruction(fetcher_buffer),
                         decoder_buffer)

    def test_decodeInstruction(self): 
        instruction_string = 'J J    3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4
        is_decoder_stalled = False

        fetcher_buffer = FetcherBuffer({
            'instr': instr,
            'npc': npc,
            'register_file': register_file,
        })

        self.assertEqual(decode_stage.DecodeStage.decode_instruction(fetcher_buffer, True), 
                         {})

        fetcher_buffer.instr = None
        self.assertEqual(decode_stage.DecodeStage.decode_instruction(fetcher_buffer), {})

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DecodeStageTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
