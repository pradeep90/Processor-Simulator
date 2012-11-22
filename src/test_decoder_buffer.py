#!/usr/bin/python

import decoder_buffer
import unittest

class DecoderBufferTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_eq(self): 
        # The bug was that DecoderBuffer was overriding the __eq__
        # method. Bad boy.
        dict1 = {'rt': None, 'rs': None, 'instr': None, 'npc': None, 
                 'PC': None, 'immediate': None} 
        dict2 = {'rt': None, 'PC': None, 'rs': None, 'npc': None, 'instr': None}
        buff1 = decoder_buffer.DecoderBuffer(dict1)
        buff2 = decoder_buffer.DecoderBuffer(dict2)
        self.assertEqual(buff1, buff2)

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DecoderBufferTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
