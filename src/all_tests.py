#!/usr/bin/python

import test_memory
import test_processor
import test_instruction
import unittest

if __name__ == '__main__':
    test_suites = [
        test_memory.get_suite(),
        test_processor.get_suite(),
        test_instruction.get_suite(),
        ]
    
    all_tests = unittest.TestSuite(test_suites)
    unittest.TextTestRunner(verbosity=2).run(all_tests)
