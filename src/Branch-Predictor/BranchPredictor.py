class BranchPredictor:
    """A n bit branch predictor has 2^n states. Half of which
    say take branch half of which say don't take it."""

    def __init__ (self, size):
        self.max = 2**size - 1
        self.taken_count = 0

    def branchTaken (self):
        self.taken_count = min (self.taken_count + 1,
                                self.max)

    def branchNotTaken (self):
        self.taken_count = max (self.taken_count - 1,
                                0)

    def predict (self):
        if self.taken_count >= (self.max + 1)/ 2 :
            return 1            # Take the branch
        else :
            return 0

