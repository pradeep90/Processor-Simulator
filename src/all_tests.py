#!/usr/bin/python

import test_memory
import test_processor
import test_instruction
import test_stage_buffer
import test_fetcher_buffer
import test_fetch_input_buffer
import test_fetch_stage
import test_decode_stage
import unittest

if __name__ == '__main__':
    test_suites = [
        test_memory.get_suite(),
        test_processor.get_suite(),
        test_instruction.get_suite(),
        test_stage_buffer.get_suite(),
        test_fetcher_buffer.get_suite(),
        test_fetch_input_buffer.get_suite(),
        test_fetch_stage.get_suite(),
        test_decode_stage.get_suite(),
        ]
    
    all_tests = unittest.TestSuite(test_suites)
    unittest.TextTestRunner(verbosity=2).run(all_tests)
