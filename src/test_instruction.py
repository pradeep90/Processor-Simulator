#!/usr/bin/python

import Instruction
import Memory
import unittest
from pprint import pprint

class InstructionTest(unittest.TestCase):
    
    def setUp(self):
        # self.instruction = Instruction.Instruction()
        pass

    def tearDown(self):
        pass

    def test___str__(self):
        bin_string = Memory.Memory.get_bin_from_hex_instruction('AC860000')
        instruction = Instruction.Instruction(bin_string)
        self.assertEqual(instruction.__str__(),
                         'SW R4 R6 0')

    def test_eq(self):
        bin_string = Memory.Memory.get_bin_from_hex_instruction('AC860000')
        instruction1 = Instruction.Instruction(bin_string)
        instruction2 = Instruction.Instruction(bin_string)
        self.assertEqual(instruction1, instruction2)
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(InstructionTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
