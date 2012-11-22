from stage_buffer import StageBuffer
from pprint import pprint

class DecoderBuffer(StageBuffer):
    """Buffer to store output of Decode stage.
    """
    arg_list = [
        'instr',
        'npc',
        'rs',
        'rt',
        'PC',
        ]
    
    def __init__(self, input_dict = {}):
        """
        """
        super(DecoderBuffer, self).__init__(input_dict)
    
    def __str__(self, ):
        """
        """
        return str(self.__dict__)

    def __repr__(self, ):
        """
        """
        return self.__str__()
