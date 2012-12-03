#!/usr/bin/python

# Sujeet Gholap <sujeet@cse.iitm.ac.in>
# CS09B010

import sys, getopt
import time

from BranchTargetBuffer import BranchTargetBuffer

def help_message():
    print "Usage:"
    print sys.argv[0] + " -f <trace file name>",
    print "-e <number of entries in BTB>"

class BranchPredictor:

    def __init__(self, argv):
        self.cold_misses = 0
        self.num_branches = 0
        self.btb_hit_count = 0
        self.num_of_btb_entries = 1
        self.file_name = 'BranchHistory.txt'
        self.parseCommandLineArgs(argv)
        self.history_file = file(self.file_name, 'r')
        self.findCommonBranch(self.history_file)
        self.trace_file = file(self.file_name, 'r')
        self.btb = BranchTargetBuffer(self.num_of_btb_entries)
        self.local_history_table = [0 for i in xrange(4)]
        self.predictors = [0 for i in xrange(4)]
        self.correct_prediction = 0

    def resetStatCounts (self) :
        self.cold_misses = 0
        self.num_branches = 0
        self.btb_hit_count = 0
        self.correct_prediction = 0

    def findCommonBranch(self, history_file):
        addresses_dict = dict()
        for line in self.history_file:
            pc_address = line.split()[0]
            if pc_address not in addresses_dict:
                addresses_dict[pc_address] = 0
            else:
                addresses_dict[pc_address] += 1

        self.common_branch = sorted(addresses_dict, key=addresses_dict.get, reverse=True)[0]

    def simulate(self) :
        addresses_dict = dict()
        self.common_branch_count = 0
        self.common_branch_correct_count = 0

        for line in self.trace_file:
            self.num_branches += 1
            split_line = line.split()

            if split_line[0] == self.common_branch:
                self.common_branch_count += 1

            pc_address = int(split_line[0], 16)
            branch_address = int(split_line[1], 16)

            # Check for BTB cold misses
            if pc_address not in addresses_dict:
                addresses_dict[pc_address] = branch_address
                self.cold_misses += 1

            btb_hit, branch_address =  self.btb.lookup(pc_address)
            if not btb_hit:
                branch_address = int(split_line[1], 16)
            else:
                self.btb_hit_count += 1

            # Prediction code
            # Look in the history table, from that value 
            # go to the predictor corresponding to that value.
            LHT_index = pc_address%4
            predictor_index = self.local_history_table[LHT_index]
            taken = self.predictors[predictor_index]
            if int(split_line[2]) == taken:
                self.correct_prediction += 1
                if split_line[0] == self.common_branch:
                    self.common_branch_correct_count += 1
            else :
                pass

            self.local_history_table[LHT_index] = (predictor_index*2 + int(split_line[2]))%4
            self.predictors[predictor_index] = int(split_line[2])
                

    def printStats(self):
        template = """\
a. BTB hit rate               : %f
b. Misprediction rate         : %f
c. Common Branch              : %s
   Common Branch contribution : %f out of %f
d. Conflict misses            : %d
e. Correct predictions        : %d"""
        values = (float (self.btb_hit_count) / self.num_branches,
                  1 - float (self.correct_prediction) / self.num_branches,
                  self.common_branch,
                  float (self.common_branch_count) / self.num_branches,
                  float (self.correct_prediction) / self.num_branches,
                  self.btb.conflict_misses,
                  self.correct_prediction)

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
                self.num_of_btb_entries = int(arg)
            elif opt in ('-f'):
                self.file_name = arg
                file_found = True
            else:
                help_message()
                sys.exit()
        
        if file_found is False:
            help_message()
            sys.exit()

if __name__ == "__main__":
    simulator = BranchPredictor(sys.argv [1:])
    simulator.simulate()
    print "First run : Cold start\n"
    simulator.printStats()
    print
    
    simulator.trace_file = file(simulator.file_name, 'r')

    simulator.resetStatCounts ()
    simulator.simulate()
    print "Second run : Warm start\n"
    simulator.printStats()
