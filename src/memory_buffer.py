from stage_buffer import StageBuffer
from pprint import pprint

class MemoryBuffer(StageBuffer):
    """Buffer to store output of Decode stage.
    """
    arg_list = [
        'instr',
        'rt',
        'rd',
        ]
    
    def __init__(self, input_dict = {}):
        """
        """
        super(MemoryBuffer, self).__init__(input_dict)
    
    def __str__(self, ):
        """
        """
        return str(self.__dict__)

    def __repr__(self, ):
        """
        """
        return self.__str__()
