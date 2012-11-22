#!/usr/bin/python

import fetcher_buffer
import Instruction
import unittest

class FetcherBufferTest(unittest.TestCase):
    def setUp(self):
        self.instruction_string = 'R ADD  R1 R2 R3'
        self.instr = Instruction.Instruction (self.instruction_string.strip().split())
        self.npc = 4
        self.PC = 0
        self.input_dict = {
            'instr': self.instr,
            'npc': self.npc,
            'PC': self.PC,
            }
        self.fetcher_buffer = fetcher_buffer.FetcherBuffer(self.input_dict)
    
    def tearDown(self):
        pass

    def test_init(self): 
        self.assertEqual(self.fetcher_buffer.instr, self.instr)
        self.assertEqual(self.fetcher_buffer.npc, self.npc)
        self.assertEqual(self.fetcher_buffer.PC, self.PC)

    def test_getitem(self): 
        for attr in self.fetcher_buffer.__dict__.keys():
            print attr
            self.assertEqual(self.fetcher_buffer[attr], 
                             self.__getattribute__(attr))

    def test_setitem(self): 
        f = fetcher_buffer.FetcherBuffer()
        for attr in self.fetcher_buffer.__dict__.keys():
            f[attr] = self.fetcher_buffer[attr]
            self.assertEqual(f[attr],
                             self.fetcher_buffer[attr])

    def test_eq(self): 
        f = fetcher_buffer.FetcherBuffer()
        f2 = fetcher_buffer.FetcherBuffer()
        self.assertEqual(f, f2)
        
        f3 = fetcher_buffer.FetcherBuffer(self.input_dict)
        self.assertEqual(f3, self.fetcher_buffer)

        buff1 = fetcher_buffer.FetcherBuffer({'foo': 123})
        buff_empty = fetcher_buffer.FetcherBuffer()
        self.assertNotEqual(buff1, buff_empty)
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FetcherBufferTest)
    return suite
    
if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
