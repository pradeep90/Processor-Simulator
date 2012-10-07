#!/usr/bin/env python

import unittest

from Memory import Memory

class MemoryTest (unittest.TestCase):

    def setUp (self):
        pass

    def test_load_program (self):
        '''Check whether the conversions of instructions into binary
        and back to hex work properly. '''
        filename = './Input_hex_fibonacci.txt'
        program_file = open (filename)
        lines = program_file.readlines ()
        program_file.close ()
        prog = '\n'.join ([line.strip ()
                           for line in lines
                           if line.strip ()])

        memory = Memory ()
        memory.loadProgram (filename)
        prog_in_memory = '\n'.join ([hex (int (instr, 2)) [2:].zfill (8).upper () [:8] for instr in memory.list])
        self.assertEqual (prog, prog_in_memory)

if __name__ == "__main__":
    unittest.main ()
