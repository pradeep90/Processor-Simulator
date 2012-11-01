class MemoryStage(object):
    """Simulator for the Memory stage of a MIPS pipeline.
    """
    
    def __init__(self, ):
        """
        """
        pass

    @staticmethod
    def doMemoryOperations (self):
        # TODO: This is where the old code did the right thing. It set
        # PC to NPC before this line and in the cases where 'instr'
        # was not in executer_buffer, the new code would simply return
        # {} and cup.
        if self.reg_writer_stalled: return {}
        if not self.executer_buffer.has_key ('instr'): 
            print 'Should PC have been changed here??'
            return {}
        instr = self.executer_buffer['instr']

        # Load : rt <- mem [imm (rs)]
        if (len (instr.opcode) == 2 and
            instr.opcode [0] in 'L'):
            mem_val = self.data_memory [self.executer_buffer ['memaddr']]

            # TODO: WHOA!!! register_file shouldn't be accessed in
            # this stage.
            self.register_file [instr.rt] = mem_val
            self.executer_buffer = {}
            return {'instr': instr,
                    'rt': [instr.rt, mem_val]}

        # Store: mem [imm (rs)] <- rt
        elif (len (instr.opcode) == 2 and
            instr.opcode [0] in 'S'):
            self.data_memory [self.executer_buffer ['memaddr']] = (
                self.executer_buffer ['rt'] [1]
            )
            self.executer_buffer = {}
            return {'instr': instr}

        temp = self.executer_buffer
        self.executer_buffer = {}
        return temp
