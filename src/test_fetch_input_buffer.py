#!/usr/bin/python

import fetch_input_buffer
import unittest

class FetchInputBufferTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FetchInputBufferTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
