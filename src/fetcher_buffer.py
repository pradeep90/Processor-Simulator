from stage_buffer import StageBuffer
from pprint import pprint

class FetcherBuffer(StageBuffer):
    """Buffer to hold output of Fetch stage.
    """

    arg_list = [
        'instr',
        'npc',
        'PC',
        ]
    
    def __init__(self, input_dict = {}):
        """
        """
        super(FetcherBuffer, self).__init__(input_dict)
