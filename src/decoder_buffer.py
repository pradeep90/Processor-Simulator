from stage_buffer import StageBuffer
from pprint import pprint

class DecoderBuffer(StageBuffer):
    """Buffer to store output of Decode stage.
    """
    arg_list = [
        'instr',
        'is_decoder_stalled',
        'register_file',
        'fetcher_buffer',
        'npc',
        'register_file',
        'rs',
        'rt',
        ]
    
    def __init__(self, input_dict = {}):
        """
        """
        super(DecoderBuffer, self).__init__(input_dict)

