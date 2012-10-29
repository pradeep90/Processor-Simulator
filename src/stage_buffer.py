class StageBuffer(object):
    """Buffer to hold input or output for a stage.
    """

    arg_list = []
    
    def __init__(self, input_dict = {}):
        """
        """
        for arg in self.arg_list:
            self.__setattr__(arg, None)

        for key in input_dict:
            self[key] = input_dict[key]
        
    def __getitem__ (self, key):
        return self.__getattribute__(key)

    def __setitem__ (self, key, value):
        return self.__setattr__(key, value)

    def __eq__(self, other):
        """Return True iff self and other have the same attributes.
        
        Arguments:
        - `other`:
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

