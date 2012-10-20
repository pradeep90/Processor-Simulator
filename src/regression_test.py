#!/usr/bin/python

import Processor
import Memory
import unittest
from pprint import pprint

class ProcessorRegressionTest(unittest.TestCase):
    
    def setUp(self):
        old_pickle_file_name = 'old-cycle-data.pickle'
        new_pickle_file_name = 'new-cycle-data.pickle'

        self.memory = Memory.Memory()
        self.memory.loadProgramDebug('fibo.txt')
        self.processor = Processor.Processor(self.memory, 0)
        self.processor.start(new_pickle_file_name)

        print
        print 'Processor Regression Testing...'
        self.old_data_list = Processor.Processor.read_saved_data(old_pickle_file_name)
        self.new_data_list = Processor.Processor.read_saved_data(new_pickle_file_name)

    def tearDown(self):
        pass
    
    def test_old_and_new_data(self):
        """Test against old intermediate output.
        """
        for cycle_num in xrange(1, len(self.old_data_list)):
            new_cycle_dict = self.new_data_list[cycle_num]
            old_cycle_dict = self.old_data_list[cycle_num]
            for key in old_cycle_dict:
                self.assertEqual(new_cycle_dict[key],
                                 old_cycle_dict[key],
                    'Failed while testing {0}. {1} != {2}'.format(
                        key, 
                        str(new_cycle_dict[key]), str(old_cycle_dict[key])
                        ))
    
def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorRegressionTest)
    return suite

if __name__ == '__main__':
    suite = get_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
