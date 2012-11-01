from memory_buffer import MemoryBuffer

class WriteBackStage(object):
    """Simulator for the Memory stage of a MIPS pipeline.
    """
    
    def __init__(self, memory_buffer, register_file):
        """Set memory_buffer and register_file for WriteBackStage.
        """
        self.memory_buffer = memory_buffer
        self.register_file = register_file

    def write_back(self):
        if self.memory_buffer.instr is None: 
            return

        instr = self.memory_buffer.instr

        # Mark the output registers clean.
        if instr.type == 'R':
            self.register_file.setClean (instr.rd)
        elif instr.type == 'I':
            self.register_file.setClean (instr.rt)

        self.memory_buffer = MemoryBuffer()
