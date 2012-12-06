class CommitStage(object):
    """Commit Stage of the MIPS pipeline.
    """
    
    def __init__(self, ROB):
        """
        """
        self.ROB = ROB

    def trigger_clock(self):
        """Commit the head instruction in ROB.
        """ 
        # TODO Branch instruction with misprediction
        self.ROB.commitInstr()
