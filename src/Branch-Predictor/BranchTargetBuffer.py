class BranchTargetBuffer:

    def __init__ (self, size):
        self.size = size
        self.buffer = [[]] * self.size
        # buffer [i] gives [instruction_addr, branch_target]
        self.resetCounters ()

    def getTarget (self, instruction_addr):
        index = instruction_addr % self.size
        pair = self.buffer [index]
        self.num_accesses += 1
        if pair and pair [0] == instruction_addr :
            return pair [1]
        else :
            if pair :
                self.conflict_miss_count += 1
            self.total_miss_count += 1
            raise Exception ("BTB miss")

    def load (self, instruction_addr, target_addr):
        index = instruction_addr % self.size
        self.buffer [index] = [instruction_addr,
                               target_addr]

    def resetCounters (self):
        self.seen_addrs = set ()
        self.conflict_miss_count = 0
        self.total_miss_count = 0
        self.num_accesses = 0

