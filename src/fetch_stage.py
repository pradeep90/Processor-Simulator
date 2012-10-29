from fetcher_buffer import FetcherBuffer
from Instruction import Instruction

class FetchStage(object):
    """Simulator for Fetch stage of MIPS Processor.
    """
    
    def __init__(self, ):
        """
        """
        pass
        
    @staticmethod
    def fetch_instruction (fetch_input_buffer = None, 
                           is_decoder_stalled = False):
        """Based on PC value, fetch instruction from memory.

        Update PC.
        Return fetcher_buffer for the next cycle.

        Arguments:
        - fetch_input_buffer: contains
          + PC
          + memory
          + is_branch_reg_zero
          + branch_target_pc
          + register_file
          + instr_count

        TODO: Take in and pass on the register_file.
        """
        if is_decoder_stalled:
            return FetcherBuffer({})
        try:
            memory = fetch_input_buffer['memory']
            PC = fetch_input_buffer['PC']
            instr_count = fetch_input_buffer['instr_count']

            IR = memory [PC]

            # Is the NPC even needed anymore?
            # PC = NPC
            NPC = PC + 4
            print 'NPC changed to', NPC

            instr_count += 1
            return FetcherBuffer({
                'instr': Instruction (IR),
                'npc': NPC,
                'PC': PC
                })
        except IndexError:
            # warn('IndexError in fetchInstruction')
            return {}
