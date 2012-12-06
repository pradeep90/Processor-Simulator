from func_unit import *
from load_store_unit import *

class ExecuteModule(object):
    """Class containing all the functional units used in Execution.
    """
    
    def __init__(self, Memory, CDB, ROB):
        """
        """
        self.Memory = Memory
        self.CDB = CDB
        self.ROB = ROB

        # NOTE: If you add any func unit, also add it in reset function and 
        # update and write function.
        self.FP_ADD = FuncUnit(2, self.CDB, 3)
        self.FP_MUL = FuncUnit(3, self.CDB, 2)
        self.BranchFU = FuncUnit(1, self.CDB, 3)
        self.Int_Calc = FuncUnit(1, self.CDB, 5)
        self.LoadStore = LoadStoreUnit(self.Memory, self.CDB, self.ROB, 4)
        self.load_step_1_done = False

