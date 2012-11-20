from memory_buffer import MemoryBuffer
from executer_buffer import ExecuterBuffer

class MemoryStage(object):
    """Simulator for the Memory stage of a MIPS pipeline.
    """

    is_stalled = False
    
    def __init__(self, executer_buffer, memory_buffer, data_memory):
        """Set the executer_buffer and memory_buffer for the Memory Stage.
        """
        self.executer_buffer = executer_buffer
        self.memory_buffer = memory_buffer
        self.data_memory = data_memory


    def do_memory_operation(self, is_writeback_stalled = False):
        """Load/Store values to/from memory.

        Else, don't do anything in this stage.
        """
        # TODO: This is where the old code did the right thing. It set
        # PC to NPC before this line and in the cases where 'instr'
        # was not in executer_buffer, the new code would simply return
        # {} and cup.

        if is_writeback_stalled or self.executer_buffer.instr is None: 
            self.memory_buffer = MemoryBuffer()
            return

        self.is_stalled = False
        instr = self.executer_buffer.instr

        # Load : rt <- mem [imm (rs)]
        if (len (instr.opcode) == 2 and
            instr.opcode [0] in 'L'):

            mem_val = self.data_memory [self.executer_buffer.memaddr]

            self.executer_buffer = ExecuterBuffer()
            self.memory_buffer.update({
                'instr': instr,
                'rt': [instr.rt, mem_val]
                })
        # Store: mem [imm (rs)] <- rt
        elif (len (instr.opcode) == 2 and
              instr.opcode [0] in 'S'):
            self.data_memory[self.executer_buffer.memaddr] = self.executer_buffer.rt[1]
            
            self.executer_buffer = ExecuterBuffer()
            self.memory_buffer.update({
                'instr': instr,
                })
        else:
            # Non-memory instructions
            self.is_stalled = False
            self.memory_buffer.update({
                'instr': instr,
                'rd': self.executer_buffer.rd,
                })
