class ExecuteStage(object):
    """Execute Stage of the MIPS pipeline.
    """
    
    def __init__(self, execute_module, CDB, ROB):
        """
        """
        self.execute_module = execute_module
        self.CDB = CDB
        self.ROB = ROB

    def trigger_clock(self):
        """Execute one cycle of each FuncUnit.

        Initially, update the ROB and every RS with values from CDB.
        """ 
        # print "RS Updates being called"
        self.execute_module.FP_ADD.update_RS()
        self.execute_module.FP_MUL.update_RS()
        self.execute_module.Int_Calc.update_RS()
        self.execute_module.LoadStore.update_RS()
        self.execute_module.BranchFU.update_RS()

        # print "CDB print"
        # print self.CDB
        self.ROB.update()

        del self.CDB[:] # Just to be safe in ROB
        self.execute_module.FP_ADD.execute()
        self.execute_module.FP_MUL.execute()
        self.execute_module.Int_Calc.execute()
        self.execute_module.BranchFU.execute()
        # print 'step1 value as arg', self.execute_module.load_step_1_done
        self.execute_module.load_step_1_done = self.execute_module.LoadStore.execute(self.execute_module.load_step_1_done)
        # print 'step1 value returned', self.execute_module.load_step_1_done
