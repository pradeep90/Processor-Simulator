from stage_buffer import StageBuffer
from pprint import pprint

class ExecuterBuffer(StageBuffer):
    """Buffer to store output of Decode stage.
    """
    arg_list = [
        'instr',
        'is_executer_stalled',
        'memaddr',
        'npc',
        'rt',
        'rd',
        ]
    
    def __init__(self, input_dict = {}):
        """
        """
        super(ExecuterBuffer, self).__init__(input_dict)

    def __eq__(self, other):
        """Return True iff self and other have the same attributes.
        
        Arguments:
        - `other`:
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __str__(self, ):
        """
        """
        return str(self.__dict__)

    def __repr__(self, ):
        """
        """
        return self.__str__()
