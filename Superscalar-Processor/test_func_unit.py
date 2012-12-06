#!/usr/bin/python

import func_unit
from exe_module import *
from pprint import pprint
import unittest

class FuncUnitTest(unittest.TestCase):
    def setUp(self):
        self.func_unit = func_unit.FuncUnit(2, [], 10)
        RS_entry_1 = {
            'Busy': True,
            'Vj': 7,
            'Vk': 8,
            'Qj': 1,
            'Qk': 0,
            'Dest': 0,
            'A': 0,
            'func': add,
            }
        RS_entry_2 = RS_entry_1.copy()
        RS_entry_3 = RS_entry_1.copy()
        RS_entry_4 = RS_entry_1.copy()
        RS_entry_5 = RS_entry_1.copy()
        self.func_unit.RS = [RS_entry_1, RS_entry_2, RS_entry_3, RS_entry_4, RS_entry_5]
    
    def tearDown(self):
        pass
    
    def test_insert_into_RS_full(self): 
        self.func_unit.RS_max_size = 3
        self.func_unit.RS = [1, 2, 3]
        actual = self.func_unit.insert_into_RS({'yo': 'boyz'})
        self.assertEqual(-1, actual)

    def test_insert_into_RS(self): 
        self.func_unit.RS = [1, 2, 3]
        temp_dict = {'yo': 'boyz'}
        actual = self.func_unit.insert_into_RS(temp_dict)
        self.assertEqual(4, actual)
        self.assertEqual('boyz', self.func_unit.RS[-1]['yo'])
        temp_dict['yo'] = 'something else'
        self.assertEqual('boyz', self.func_unit.RS[-1]['yo'])

    def test_execute(self): 
        self.func_unit.RS[2]['Qj'] = 0
        self.func_unit.RS[4]['Qj'] = 0

        self.func_unit.execute()

        # Only the first ready instruction (#2 in this case) should be
        # executed
        self.assertEqual(4, len(self.func_unit.RS))
        self.assertEqual([7, 8, 0, 0, add], self.func_unit.op_queue[-1])

    def test_update_RS(self): 
        for i, RS_entry in enumerate(self.func_unit.RS):
            RS_entry['Qj'] = i
        pprint('self.func_unit.RS: ')
        pprint(self.func_unit.RS)
        
        CDB_elem_1 = [17, 2]
        CDB_elem_2 = [2724, 4]
        CDB_elem_3 = [99, 2]
        
        self.func_unit.CDB = [CDB_elem_1, CDB_elem_2, CDB_elem_3]
        self.func_unit.update_RS()

        for i in [0, 1, 3]:
            self.assertEqual(i, self.func_unit.RS[i]['Qj'])

        self.assertEqual(0, self.func_unit.RS[2]['Qj'])
        self.assertEqual(0, self.func_unit.RS[4]['Qj'])

        # Latest value should be taken (99 vs 2724)
        self.assertEqual(99, self.func_unit.RS[2]['Vj'])
        self.assertEqual(2724, self.func_unit.RS[4]['Vj'])

    def test_write_results_to_CDB(self): 
        op_elem_1 = [7, 8, 0, 0, add]
        op_elem_2 = [5, 5, 7, 0, sub]
        self.func_unit.op_queue = [op_elem_1, op_elem_2]

        self.func_unit.write_results_to_CDB()
        self.assertEqual(1, self.func_unit.op_queue[1][3])
        self.assertEqual(1, self.func_unit.op_queue[0][3])

        op_elem_3 = [5, 5, 6, 0, sub]
        self.func_unit.op_queue.append(op_elem_3)

        self.func_unit.write_results_to_CDB()

        self.assertEqual(1, len(self.func_unit.op_queue))
        self.assertEqual([[15, 0], [0, 7]], self.func_unit.CDB)
        
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(FuncUnitTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
