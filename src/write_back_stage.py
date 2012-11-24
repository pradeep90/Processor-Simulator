from memory_buffer import MemoryBuffer
from pipeline_stage import PipelineStage

class WriteBackStage(PipelineStage):
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
            self.register_file[self.memory_buffer.rd[0]] = self.memory_buffer.rd[1]
        elif instr.type == 'I':
            if instr.opcode in ['BEQ', 'BNE', 'SW']:
                pass
            else:
                self.register_file.setClean (instr.rt)
                self.register_file[self.memory_buffer.rt[0]] = self.memory_buffer.rt[1]

        self.memory_buffer.clear()
