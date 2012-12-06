class RegFile(object):
    def __init__(self, size):
        self.registers = [{
            'Value': 0, 
            'Busy': False, 
            'ROB_index': 0} for i in xrange(size)] 
