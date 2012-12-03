class History :
    """History is represented as a sequence of 'size' number
    of bits. Implemented as a queue."""

    def __init__ (self, size):
        self.queue = [0] * size

    def branchTaken (self):
        self.queue = self.queue [1:] + [1]

    def branchNotTaken (self):
        self.queue = self.queue [1:] + [0]

    def getNumericValue (self):
        string = "".join (str(bit) for bit in self.queue)
        return int(string, 2)

