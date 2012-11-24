class PipelineStage(object):
    """Class to simulate a Pipeline Stage.
    """

    is_stalled = False
    num_stalls = 0
    
    def __init__(self, **other_stages):
        """
        """
        pass

    def stall(self, ):
        """Become stalled.
        """
        self.is_stalled = True
        self.incr_stalls()

    def unstall(self, ):
        """Become unstalled.
        """
        self.is_stalled = False
    
    def incr_stalls(self, ):
        """Increment stalls.
        """
        self.num_stalls += 1

