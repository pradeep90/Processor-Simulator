#!/usr/bin/python

import Processor
import Memory
import Instruction
import unittest
from RegisterFile import RegisterFile
from pprint import pprint

class ProcessorTest(unittest.TestCase):
    
    def setUp(self):
        
        hex_instruction_list = [
            '00001020',                   # I instruction
            '00011820',
            '00432020',
            '00A12822',
            '00031025',                   # R instruction
            '00041825',
            'AC860000',
            '20C60001',
            '1005000A',
            '08000002', 
            ]

        # Actual Code:
        # I ADDI R1 R1 1
        # I ADDI R2 R2 2
        # I ADDI R5 R5 89
        # I BEQ  R2 R5 4
        # R ADD  R1 R2 R3
        # R ADD  R2 R0 R1
        # R ADD  R3 R0 R2
        # J J    3
        # I ADDI R9 R9 999
        
        bin_instruction_list = [
            Memory.Memory.get_bin_from_hex_instruction(instruction) 
            for instruction in hex_instruction_list]
        self.memory = Memory.Memory(bin_instruction_list)
        self.register_file = RegisterFile()
        self.processor = Processor.Processor(self.memory, 0)

    def tearDown(self):
        pass

    def test_fetch_instruction(self):
        fetch_input_buffer = {'is_decoder_stalled': True}
        self.assertEqual(self.processor.fetch_instruction(fetch_input_buffer),
                         {})

        fetch_input_buffer = {'memory': self.memory,
                              'PC': 0,
                              'instr_count': 0,
                              }
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
        self.assertEqual(self.processor.decode_R_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rd))

        register_file.setDirty(instr.rt)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(self.processor.decode_R_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rd))

    def test_decode_I_instruction(self):
        instruction_string = 'R ADD  R1 R2 R3'
        instr = Instruction.Instruction (self.memory[0])
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
            'rs': [instr.rs, self.register_file [instr.rs]],
            'rt': [instr.rt, self.register_file [instr.rt]],
            'npc': npc,
            }
        self.assertEqual(self.processor.decode_R_instruction(fetcher_buffer),
                         decoder_buffer)
        register_file.setDirty(instr.rt)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(self.processor.decode_R_instruction(fetcher_buffer),
                         decoder_buffer)
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
