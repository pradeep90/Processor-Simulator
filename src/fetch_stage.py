from fetcher_buffer import FetcherBuffer
from Instruction import Instruction

class FetchStage(object):
    """Simulator for Fetch stage of MIPS Processor.
    """
    
    def __init__(self, memory, fetch_input_buffer, fetcher_buffer):
        """
        TODO: Take in instr_count
        """
        self.memory = memory
        self.fetch_input_buffer = fetch_input_buffer
        self.fetcher_buffer = fetcher_buffer
        
    def fetch_instruction (self, is_decoder_stalled = False):
        """Based on PC value, fetch instruction from memory.

        Update PC.
        Return fetcher_buffer for the next cycle.

        TODO: Update instr_count
        """
        if is_decoder_stalled:
            self.fetcher_buffer = FetcherBuffer({})
            return

        try:
            self.fetcher_buffer.instr = Instruction(
                self.memory[self.fetch_input_buffer.PC])
            self.fetcher_buffer.PC = self.fetch_input_buffer.PC
            self.fetcher_buffer.npc = self.fetcher_buffer.PC + 4
            self.fetch_input_buffer.PC = self.fetcher_buffer.npc
            self.fetch_input_buffer.instr_count += 1
        except IndexError:
            self.fetcher_buffer = FetcherBuffer()
