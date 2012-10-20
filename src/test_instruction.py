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

    # TODO
    # def test_get_binary_reprn_of_HR_instruction(self):
    #     instruction_list = [
    #         'I BEQ  R2 R5 4',
    #         'R ADD  R1 R2 R3',
    #         'R ADD  R2 R0 R1',
    #         'R ADD  R3 R0 R2',
    #         'J J    3',
    #         ]
    #     binary_instruction_list = [
    #         '',
    #         '',
    #         '',
    #         '',
    #         '',
    #         ]

    #     # instruction_list = [instruction.split() for instruction in instruction_list]
    #     for binary_instruction, instruction in zip(binary_instruction_list, 
    #                                                instruction_list):
    #         self.assertEqual(
    #             Instruction.Instruction.get_binary_reprn_of_HR_instruction(instruction), 
    #             binary_instruction)

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(InstructionTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
