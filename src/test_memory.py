#!/usr/bin/python

import Memory
import unittest
from pprint import pprint

class MemoryTest(unittest.TestCase):
    
    def setUp(self):
        hex_instruction_list = [
            '00001020',
            '00011820',
            '00432020',
            '00A12822',
            '00031025',
            '00041825',
            'AC860000',
            '20C60001',
            '1005000A',
            '08000002', 
            ]
        
        bin_instruction_list = [
            Memory.Memory.get_bin_from_hex_instruction(instruction) 
            for instruction in hex_instruction_list]
        self.memory = Memory.Memory(bin_instruction_list)

    def tearDown(self):
        pass

    def test_get_binary_string(self): 
        integer = 7
        self.assertEqual(Memory.Memory.get_binary_string(integer), 
                         '00000000000000000000000000000111')
        self.assertEqual(Memory.Memory.get_binary_string(integer, 8), 
                         '00000000000000000000000000000111'[-8:])

    def test_get_bin_from_hex_instruction(self):
        hex_string = '0x343'
        bin_string = '00000000000000000000001101000011'

        self.assertEqual(bin_string, 
                         Memory.Memory.get_bin_from_hex_instruction(hex_string))

    def test_invalid_memory_index(self):
        self.assertRaises(IndexError, self.memory.__getitem__, 1000)

    def test_load_program (self):
        '''Check whether the conversions of instructions into binary
        and back to hex work properly. 

        Sujeet's test.
        '''
        filename = './Input_hex_fibonacci.txt'
        program_file = open (filename)
        lines = program_file.readlines ()
        program_file.close ()
        prog = '\n'.join ([line.strip ()
                           for line in lines
                           if line.strip ()])

        memory = Memory.Memory ()
        memory.loadProgram (filename)
        prog_in_memory = '\n'.join ([hex (int (instr, 2)) [2:].zfill (8).upper () [:8] 
                                     for instr in memory.list])
        self.assertEqual (prog, prog_in_memory)
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(MemoryTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
