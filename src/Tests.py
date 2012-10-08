#!/usr/bin/env python

import unittest
import sys

from Memory import Memory
from Processor import Processor

original_stdout = sys.stdout

class NullDevice():
    def write(self, s):
        pass

def disablePrint ():
    sys.stdout = NullDevice ()

def enablePrint ():
    sys.stdout = original_stdout

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

class ProcessorTest (unittest.TestCase):

    def setUp (self):
        pass

    def test_single_instr (self):
        prog = "I ADDI R1 R1 8"
        memory = Memory ()
        memory.loadProgramDebugFromText (prog)
        processor = Processor (memory, 0)
        disablePrint ()
        processor.start ()
        enablePrint ()
        cpi = processor.getCPI ()
        r1_content = processor.register_file [1]
        self.assertEqual (cpi, 5)
        self.assertEqual (r1_content, 8)

    def test_dependant_instrs_dummy (self):
        prog = """I ADDI R1 R1 1
R ADD  R1 R1 R2
"""
        memory = Memory ()
        memory.loadProgramDebugFromText (prog)
        processor = Processor (memory, 0)
        disablePrint ()
        processor.start ()
        enablePrint ()
        cpi = processor.getCPI ()
        # CPI should be 4 because there stall of length 2
        # For the second instruction.
        self.assertEqual (cpi, 4)

    def test_independant_instrs_dummy (self):
        prog = """I ADDI R1 R1 1
R ADD  R3 R3 R2
"""
        memory = Memory ()
        memory.loadProgramDebugFromText (prog)
        processor = Processor (memory, 0)
        disablePrint ()
        processor.start ()
        enablePrint ()
        cpi = processor.getCPI ()
        # CPI should be 3 as there is no stall
        # For the second instruction.
        self.assertEqual (cpi, 3)

if __name__ == "__main__":
    unittest.main ()
