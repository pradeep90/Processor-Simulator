#!/usr/bin/python

import load_store_unit
from exe_module import *
from operations import *
from pprint import pprint
from ROB import ROB
import unittest

class LoadStoreUnitTest(unittest.TestCase):
    def setUp(self):
        self.CDB = []
        self.ROB = ROB(10, self.CDB, None, None, None)
        self.load_store_unit = load_store_unit.LoadStoreUnit(None, self.CDB, self.ROB, 10)

        load_entry_1 = {
            'Busy': True,
            'Vj': 7,
            'Vk': 8,
            'Qj': 1,
            'Qk': 0,
            'Dest': 3,
            'A': 44,
            'func': is_load,
            'ROB_index': 8,
            }
        load_entry_2 = load_entry_1.copy()
        load_entry_3 = load_entry_1.copy()
        load_entry_4 = load_entry_1.copy()
        load_entry_5 = load_entry_1.copy()
        self.load_store_unit.RS = [load_entry_1, load_entry_2, load_entry_3, 
                                   load_entry_4, load_entry_5]  

    def tearDown(self):
        pass
    
    def test_write_data_to_CDB_load(self): 
        self.load_store_unit.RS[2]['Busy'] = False
        self.load_store_unit.RS[2]['Qj'] = 0
        self.load_store_unit.RS[4]['Busy'] = False
        self.load_store_unit.RS[4]['Qj'] = 0
        self.load_store_unit.RS[4]['Dest'] = 7

        self.load_store_unit.mem_value_read = 2009
        self.load_store_unit.write_data_to_CDB()

        # Only the result of RS[2] should be written to CDB
        self.assertEqual([[2009, 3]], self.load_store_unit.CDB)
        self.assertEqual(4, len(self.load_store_unit.RS))

    def test_is_load_instrn(self): 
        self.load_store_unit.RS[3]['func'] = add

        for i in [0, 1, 2, 4]:
            self.assertTrue(self.load_store_unit.is_load_instrn(i))
        self.assertFalse(self.load_store_unit.is_load_instrn(3))

    def test_write_data_to_CDB_store(self): 
        for i in xrange(5):
            # Make everything a store (not a load)
            self.load_store_unit.RS[i]['func'] = lambda x,y: 3

        self.load_store_unit.RS[2]['Qj'] = 0
        self.load_store_unit.RS[2]['Qk'] = 0
        self.load_store_unit.RS[4]['Qj'] = 0
        self.load_store_unit.RS[4]['Qk'] = 0

        self.load_store_unit.RS[4]['Dest'] = 7

        self.load_store_unit.mem_value_read = 2009
        self.load_store_unit.ROB.buffer = [{}, {}, {}]

        self.load_store_unit.write_data_to_CDB()

        # Only the result of RS[2] should be written to ROB
        self.assertEqual(8, self.load_store_unit.ROB.buffer[2]['Value'])
        self.assertTrue(self.load_store_unit.ROB.buffer[2]['Ready'])
        self.assertEqual(4, len(self.load_store_unit.RS))

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(LoadStoreUnitTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
