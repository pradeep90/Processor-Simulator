#!/usr/bin/python

import Processor
import Memory
import Instruction
import unittest
from RegisterFile import RegisterFile
from pprint import pprint
from fetcher_buffer import FetcherBuffer
from fetch_input_buffer import FetchInputBuffer

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
        # Decoder Stalled
        fetch_input_buffer = FetchInputBuffer({
            'memory': self.memory,
            'PC': 0,
            'instr_count': 0,
            })
        self.assertEqual(self.processor.fetch_instruction(fetch_input_buffer, 
                                                          True),
                         FetcherBuffer({}))

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
        self.assertEqual(self.processor.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)
        self.assertTrue(register_file.isDirty(instr.rt))

        register_file.setDirty(instr.rs)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(self.processor.decode_I_instruction(fetcher_buffer),
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
        self.assertEqual(self.processor.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)

        register_file.setDirty(instr.rs)
        decoder_buffer = {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': True,
            }
        self.assertEqual(self.processor.decode_I_instruction(fetcher_buffer),
                         decoder_buffer)

    def test_get_jump_address(self): 
        instruction_string = 'J J    3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        npc = 4
        self.assertEqual(Processor.Processor.get_jump_address(npc, instr), 12)

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
        self.assertEqual(self.processor.decode_J_instruction(fetcher_buffer),
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

        self.assertEqual(self.processor.decode_instruction(fetcher_buffer, True), 
                         {})

        fetcher_buffer.instr = None
        self.assertEqual(self.processor.decode_instruction(fetcher_buffer), {})

    def test_execute_R_instruction(self): 
        instruction_string = 'R ADD  R1 R2 R3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4

        memory = Memory.Memory([instruction_string.strip().split()])
        decoder_buffer = self.processor.get_stage_output(
            memory, register_file, 0, 0, 'decode')

        mem_buffer = {
            'register_file': register_file,
            'decoder_buffer': {},
            'is_executor_stalled': False,
            'instr': instr,
            'npc': npc,
            'rd': [instr.rd, register_file [instr.rd]],
            }
        self.assertEqual(self.processor.execute_R_instruction(decoder_buffer), 
                         mem_buffer)

        decoder_buffer.pop('rs')
        mem_buffer = {
            'register_file': register_file,
            'decoder_buffer': decoder_buffer,
            'is_executor_stalled': True,
            }
        self.assertEqual(self.processor.execute_R_instruction(decoder_buffer),
                         mem_buffer)

    # def test_execute_I_instruction(self): 
    #     instruction_list = [
    #         'I ADDI R1 R1 1',
    #         'I LW  R2 R5 4',
    #         'I BEQ  R2 R5 4',
    #     ]

    #     rt_val_list = [
    #         [1, 1],
    #         5,
    #         None,
    #     ]
    #     instruction_list = [instruction.strip().split() 
    #                         for instruction in instruction_list]
    #     register_file = self.register_file
    #     memory = Memory.Memory(instruction_list)
    #     npc = 4

    #     register_file_list = [RegisterFile()] * len(instruction_list)
    #     mem_buffer_list = [
    #         {
    #             'register_file': register_file_list[i],
    #             'decoder_buffer': {},
    #             'is_executor_stalled': False,
    #             'instr': Instruction.Instruction(memory[i * 4]),
    #             'npc': npc + i * 4,
    #             'rt': rt_val_list[i],
    #             'memaddr': 4,
    #         }
    #         for i in xrange(len(instruction_list))]

    #     for i in xrange(len(instruction_list)):
    #         decoder_buffer = self.processor.get_stage_output(
    #             memory, register_file_list[i], i * 4, 0, 'decode')
    #         actual_mem_buffer = self.processor.execute_I_instruction(decoder_buffer)
    #         pprint(actual_mem_buffer)
    #         for key in actual_mem_buffer:
    #             print key
    #             self.assertEqual(actual_mem_buffer[key], mem_buffer_list[i][key])

    def test_execute(self): 
        instruction_string = 'R ADD  R1 R2 R3'
        instr = Instruction.Instruction (instruction_string.strip().split())
        register_file = self.register_file
        npc = 4

        decoder_buffer = {
            'instr': instr,
            'npc': npc,
            'register_file': register_file,
            'is_mem_stalled': True,
        }

        self.assertEqual(self.processor.execute(decoder_buffer), {})

        decoder_buffer.pop('is_mem_stalled')
        decoder_buffer.pop('instr')
        self.assertEqual(self.processor.execute(decoder_buffer), {})

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
