#!/usr/bin/python

# Sujeet Gholap <sujeet@cse.iitm.ac.in>
# CS09B010

class BranchTargetBuffer:

    def __init__(self, num_entries):
        self.num_entries = num_entries
        self.conflict_misses = 0
        self.btb = [[0, 0] for i in xrange(num_entries)]

    def getIndex (self, address) :
        """
        Given an address, returns the index into the BTB for the
        corresponding entry.
        Will be useful in later cases when something other than direct
        mapped BTB is considered.
        """
        return address % self.num_entries

    def lookup(self, pc_address):
        """
        Looks up for the values and returns 
        True or False, and branch target. As a list.
        First is the boolean the second is the branch target.
        """
        index = self.getIndex (pc_address)
        if self.btb[index][0] == pc_address:
            return [True, self.btb[index][1]]
        else:
            return [False, self.btb[index][1]]
