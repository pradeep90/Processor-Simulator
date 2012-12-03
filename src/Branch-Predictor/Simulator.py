#!/usr/bin/python

# Sujeet Gholap <sujeet@cse.iitm.ac.in>
# CS09B010

import sys, getopt
import time

from collections import defaultdict

from BranchPredictor import BranchPredictor
from History import History
from BranchTargetBuffer import BranchTargetBuffer

def help_message():
    print "Usage:"
    print sys.argv[0] + " -f <trace file name>",
    print "-e <number of entries in BTB>"

class Simulator:
    num_bits_for_history = 3
    history_size = 4
    predictor_size = 2

    def __init__(self, argv):
        # key is instruction address
        # value is number of correct predictions
        self.correct_prediction_dict = defaultdict (lambda : 0)

        self.history_table = [History (self.history_size)
                              for foo
                              in xrange (2 ** self.num_bits_for_history)]
        self.predictors = [BranchPredictor (self.predictor_size)
                           for foo
                           in xrange (2 ** self.history_size)]

        self.parseCommandLineArgs (argv)
        self.btb = BranchTargetBuffer (self.btb_size)

        hist_file = open (self.hist_file_name)
        guess_int = lambda x : int (x, 0)

        self.hist_file_data = [map (guess_int, line.strip().split())
                               for line in hist_file.read().split('\r')
                               if line]
        hist_file.close ()

    def simulate (self):
        for addr, target, result in self.hist_file_data :
            hist_index = addr % (2 ** self.num_bits_for_history)
            history = self.history_table [hist_index]
            predictor = self.predictors [history.getNumericValue ()]
            predicted_outcome = predictor.predict ()

            if predicted_outcome == result :
                self.correct_prediction_dict [addr] += 1

            # Now update the predictor and history according to
            # actual value
            if result == 1 :
                predictor.branchTaken ()
                history.branchTaken ()
            else :
                predictor.branchNotTaken ()
                history.branchNotTaken ()

            # Simulating BTB
            try :
                self.btb.getTarget (addr)
            except :
                self.btb.load (addr, target)
            

    def resetCounters (self) :
        self.correct_prediction_dict = defaultdict (lambda : 0)
        self.btb.resetCounters ()

    def printStats(self):
        btb_hit_rate = (float (self.btb.num_accesses
                               - self.btb.total_miss_count)
                        / self.btb.num_accesses)

        num_branches = len (self.hist_file_data)
        correct_predictions = sum ([self.correct_prediction_dict [key]
                                    for key in
                                    self.correct_prediction_dict])
        misprediction_rate = 1 - float (correct_predictions) / num_branches

        counts = defaultdict (lambda : 0)
        for addr, foo, bar in self.hist_file_data :
            counts [addr] += 1
        counts = counts.items()
        counts.sort (key = lambda x : x [1],
                     reverse = True)
        most_common_branch = counts [0] [0]

        template = """\
a. BTB hit rate                      : %f
b. Misprediction rate                : %f
c. Common Branch                     : %s
   Common Branch correct predictions : %d
d. Conflict misses                   : %d
e. Correct predictions               : %d"""
        values = (btb_hit_rate,
                  misprediction_rate,
                  hex (most_common_branch),
                  self.correct_prediction_dict [most_common_branch],
                  self.btb.conflict_miss_count,
                  correct_predictions)

        print template % values
       
    def parseCommandLineArgs(self, argv):
        try:
            opts, args = getopt.getopt(argv, 'e:f:')
            
        except getopt.GetoptError:
            help_message()
            sys.exit(2)
            
        file_found = False
        for opt, arg in opts:
            if opt in ("-e"):
                self.btb_size = int(arg)
            elif opt in ('-f'):
                self.hist_file_name = arg
                file_found = True
            else:
                help_message()
                sys.exit()
        
        if file_found is False:
            help_message()
            sys.exit()

if __name__ == "__main__":
    simulator = Simulator(sys.argv [1:])
    simulator.simulate()
    print "First run : Cold start"
    simulator.printStats()
    simulator.resetCounters()
    simulator.simulate()
    print "Second run : Warm start"
    simulator.printStats()
