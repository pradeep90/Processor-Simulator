from pipeline_stage import PipelineStage

class FetchStage(PipelineStage):
    """Fetch Stage of the Pipeline.

    Simply used to get the next instruction.
    """
    
    def __init__(self, init_PC, npc_line, fetch_buffer, instruction_cache):
        """Set the PC, fetch_buffer, and instruction_cache.
        """
        self.PC = init_PC

        # Shared Next PC value (may be set elsewhere if there is a
        # misprediction, etc.)
        self.npc = npc_line
        self.index_error_count = 0
        self.fetch_buffer = fetch_buffer
        self.instr_cache = instruction_cache

    def trigger_clock(self):
        """Put the next instruction into fetch_buffer.

        fetch_buffer contains:
        + PC
        + IR

        If there is an error, increment index_error_count.
        With 5 errors, it's probably the end of the program.
        """ 
        return_value = 0
        self.PC = self.npc[0]
        try:
            self.fetch_buffer['IR'] = self.instr_cache[self.PC/4]
            self.fetch_buffer['PC'] = self.PC
            self.index_error_count = 0
        except IndexError:
            self.index_error_count += 1
            if self.index_error_count == 5:
                return_value = -77
            else: 
                self.fetch_buffer['IR'] = '0x00000000'
                return_value = -1

        self.npc[0] = self.PC + 4
        return return_value
