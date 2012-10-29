class WriteBackStage(object):
    """Simulator for the Memory stage of a MIPS pipeline.
    """
    
    def __init__(self, ):
        """
        """
        pass

    def writeBackRegisters (self):
        if not self.memory_buffer.has_key ('instr'): return {}
        instr = self.memory_buffer ['instr']

        # Mark the output registers clean.
        if instr.type == 'R':
            self.register_file.setClean (instr.rd)
        elif instr.type == 'I':
            self.register_file.setClean (instr.rt)

        self.memory_buffer = {}
