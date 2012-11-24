#!/usr/bin/python

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

class ProcessorTest(unittest.TestCase):
    
    def setUp(self):
        instruction_list = [
            'I ADDI R1 R1 1',
            'I ADDI R2 R2 2',
            'I ADDI R5 R5 89',
            'I BEQ  R2 R5 4',
            'R ADD  R1 R2 R3',
            'R ADD  R2 R0 R1',
            'R ADD  R3 R0 R2',
            'J J    3',
            'I ADDI R9 R9 999',
            ]
        instruction_list = [instruction_string.split()
                            for instruction_string in instruction_list]
        self.memory = Memory.Memory(instruction_list)
        self.register_file = RegisterFile()
        self.processor = Processor.Processor(self.memory, 0)

    # def test_execute_one_cycle(self): 
    #     self.processor.execute_one_cycle()
    #     print self.register_file
    #     self.processor.print_buffers()

    # def test_are_instructions_in_flight(self): 
    #     self.assertFalse(self.processor.are_instructions_in_flight())

    #     self.processor.decode_stage.is_stalled = True
    #     self.assertTrue(self.processor.are_instructions_in_flight())
    #     self.processor.decode_stage.is_stalled = False

    #     self.processor.execute_one_cycle()
    #     self.assertTrue(self.processor.are_instructions_in_flight())

    # def test_execute_cycles(self): 
    #     self.processor.execute_cycles(1)
    #     print self.register_file
    #     self.processor.print_buffers()

    def test_all_intermediate_buffers_are_shared(self): 
        for i in xrange(1, 10):
            processor = Processor.Processor(self.memory, 0)
            processor.execute_cycles(i)
            pairs = [
                (processor.fetch_stage.fetcher_buffer, 
                 processor.decode_stage.fetcher_buffer),
                (processor.decode_stage.decoder_buffer, 
                 processor.execute_stage.decoder_buffer),
                (processor.execute_stage.executer_buffer, 
                 processor.memory_stage.executer_buffer),
                (processor.memory_stage.memory_buffer, 
                 processor.write_back_stage.memory_buffer),
                ]
            for i, pair in enumerate(pairs):
                self.assertEqual(pair[0], pair[1], '{0} != {1} index: {2}'.format(pair[0], pair[1], i))
        
    def test_execute_cycles_BEQ_true(self): 
        instruction_list = [
            'I BEQ  R2 R5 4',
            'R ADD  R1 R2 R3',
            'R ADD  R1 R2 R3',
            'R ADD  R2 R0 R1',
            'R ADD  R3 R0 R2',
            'J J    3',
            'I ADDI R9 R9 999',
            ]
        instruction_list = [instruction_string.split()
                            for instruction_string in instruction_list]
        memory = Memory.Memory(instruction_list)
        processor = Processor.Processor(memory, 0)
        processor.execute_cycles(3)
        self.assertEqual(processor.execute_stage.branch_pc, 20)
        self.assertEqual(processor.fetch_stage.fetch_input_buffer.PC, 20)

        self.assertEqual(processor.executer_buffer, ExecuterBuffer())
        self.assertEqual(processor.decoder_buffer, DecoderBuffer())
        self.assertEqual(processor.fetcher_buffer, FetcherBuffer())

    def test_operand_forwarding_ALU(self): 
        # Expected output:
        # R1 = 8, R4 = 8
        # (R4) <- R5 = 9
        # R2 <- (R1) = 9
        instruction_list = [
            'I ADDI R5 R5 9',
            'I ADDI R2 R2 3',
            'I ADDI R3 R3 5',
            'I ADDI R4 R4 8',
            'I ADDI R6 R6 9',
            'R ADD  R2 R3 R1',
            'I LW  R1 R2 0',
            ]
            # # Later
            # 'I SW  R1 R5 0',
        instruction_list = [instruction_string.split()
                            for instruction_string in instruction_list]
        memory = Memory.Memory(instruction_list)
        processor = Processor.Processor(memory, 0)
        processor.start()
        print 'CPI: ', processor.getCPI ()
        self.assertEqual(processor.decode_stage.num_stalls, 2)
        self.assertEqual(processor.execute_stage.num_stalls, 0)
        self.assertEqual(processor.memory_stage.num_stalls, 0)

    # def test_operand_forwarding_R_and_R_instruction(self): 
    #     instruction_list = [
    #         'I ADDI R2 R2 3',
    #         'I ADDI R3 R3 5',
    #     # Filler
    #         'I ADDI R6 R6 9',
    #         'I ADDI R7 R7 9',
    #         'I ADDI R8 R8 9',
    #         'R ADD  R2 R3 R2',
    #         'R ADD  R2 R3 R1',
    #         ]
    #         # # Later
    #         # 'I SW  R1 R5 0',
    #     instruction_list = [instruction_string.split()
    #                         for instruction_string in instruction_list]
    #     memory = Memory.Memory(instruction_list)
    #     processor = Processor.Processor(memory, 0)
    #     processor.start()
    #     print 'CPI: ', processor.getCPI ()
    #     self.assertEqual(processor.decode_stage.num_stalls, 0)
    #     self.assertEqual(processor.execute_stage.num_stalls, 0)
    #     self.assertEqual(processor.memory_stage.num_stalls, 0)

    def tearDown(self):
        pass

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
