from stage_buffer import StageBuffer

class FetchInputBuffer(StageBuffer):
    """Buffer for storing input to the Fetch stage.
    """

    arg_list = [
        'PC',
        'is_branch_reg_zero',
        'branch_target_pc',
        'instr_count',
        ]
    
    def __init__(self, input_dict = {}):
        """
        """
        super(FetchInputBuffer, self).__init__(input_dict)

    def __eq__(self, other):
        """Return True iff self and other have the same attributes.
        
        Arguments:
        - `other`:
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __repr__(self, ):
        """
        """
        return self.__str__() 

    def __str__(self, ):
        """
        """
        return str(self.__dict__)

