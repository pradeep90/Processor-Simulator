class WriteStage(object):
    """Write stage of the MIPS pipeline.
    """
    
    def __init__(self, execute_module):
        """
        """
        self.execute_module = execute_module

    def trigger_clock(self):
        """Write the results of execution to the CDB.
        """ 
        self.execute_module.FP_ADD.write_results_to_CDB()
        self.execute_module.FP_MUL.write_results_to_CDB()
        self.execute_module.Int_Calc.write_results_to_CDB()
        self.execute_module.LoadStore.write_results_to_CDB()
        self.execute_module.BranchFU.write_results_to_CDB()
        
