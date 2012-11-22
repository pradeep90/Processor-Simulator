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

    def is_empty(self, ):
        """Return True iff all attributes of the Buffer are None.
        """
        return all(self.__getattribute__(k) == None for k in self.__dict__)

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
            is_self_empty = all(self[key] is None for key in self.__dict__) 
            is_other_empty = all(other[key] is None for key in other.__dict__)

            if is_self_empty or is_other_empty:
                # They may have differing properties, but they must
                # all be None
                return is_self_empty and is_other_empty
            else:
                return self.__dict__ == other.__dict__
        else:
            return False

    def update(self, given_dict):
        """Update buffer attributes with those in given_dict.
        
        Arguments:
        - `given_dict`:
        """
        self.__dict__.update(given_dict)

    def clear(self, ):
        """Clear buffer.
        """
        for key in self.__dict__:
            self[key] = None

    def __str__(self, ):
        """
        """
        return str(self.__dict__)

    def __repr__(self, ):
        """
        """
        return self.__str__() 
