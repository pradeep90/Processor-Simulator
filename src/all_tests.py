#!/usr/bin/python

import test_decode_stage
import test_execute_stage
import test_fetcher_buffer
import test_fetch_input_buffer
import test_decoder_buffer
import test_fetch_stage
import test_instruction
import test_memory
import test_memory_stage
import test_processor
import test_stage_buffer
import test_write_back_stage
import unittest

if __name__ == '__main__':
    test_suites = [
        test_decode_stage.get_suite(),
        test_execute_stage.get_suite(),
        test_fetch_input_buffer.get_suite(),
        test_fetch_stage.get_suite(),
        test_fetcher_buffer.get_suite(),
        test_instruction.get_suite(),
        test_memory.get_suite(),
        test_memory_stage.get_suite(),
        test_processor.get_suite(),
        test_stage_buffer.get_suite(),
        test_write_back_stage.get_suite(),
        test_decoder_buffer.get_suite(),
        ]
    
    all_tests = unittest.TestSuite(test_suites)
    unittest.TextTestRunner(verbosity=2).run(all_tests)
