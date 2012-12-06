# Helper functions

ROB_MAX_SIZE = 10
LOAD_SPECIAL_VAL = 1

def mul(a, b):
    return a*b

def div(a, b):
    return a/b

def add(a, b):
    return a+b

def sub(a, b):
    return a-b

def and_func(a, b):
    return a & b 

def or_func(a, b):
    return a | b

def nor_func(a, b):
    return ~ (a | b)

def xor_func(a, b):
    return a ^ b

def shift_left(a, b):
    return (a * (2**b))%(2**64)

def is_load(a, b):
    """Return a special value that can be used to test for Loads.""" 
    return LOAD_SPECIAL_VAL

def not_equal_to(a, b):
    return int(a != b)

def equal_to(a, b):
    return int(a == b)

