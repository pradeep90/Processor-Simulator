#!/usr/bin/python

import test_func_unit
import test_load_store_unit
import unittest

if __name__ == '__main__':
    test_suites = [
        test_func_unit.get_suite(),
        test_load_store_unit.get_suite(),
        ]
    
    all_tests = unittest.TestSuite(test_suites)
    unittest.TextTestRunner(verbosity=2).run(all_tests)
