import operator, copy
from collections import defaultdict
from func_unit import *
from load_store_unit import *
from ROB import ROB
from operations import *

ROB_MAX_SIZE = 10

def breakpoint () :
    try :
        import IPython
        return IPython.Shell.IPShellEmbed()()
    except :
        import code
        return code.interact(local=dict(globals(), **locals()))
class ExeModule:
    """Module for all the steps in Execution of an instruction.

    Steps include:
    + Issue
    + Execute
    + Write Result
    + Commit
    """
    
    def __init__(self, FPRegisterFile, IntRegisterFile,
                 controller, instr_queue, Memory, npc_line):
        """
        Create Execution Module using the various external components.

        Create an ROB and functional units like:
        + FP_ADD
        + FP_MUL
        + BranchFU
        + Integer Calculation unit
        + Load Store Unit
        """
        self.controller = controller
        self.instr_queue = instr_queue
        self.CDB = []
        self.npc_line = npc_line
        
        self.FPRegisterFile = FPRegisterFile
        self.IntRegisterFile = IntRegisterFile
        self.Memory = Memory
        
        self.ROB = ROB(ROB_MAX_SIZE, self.CDB, self.IntRegisterFile, self.Memory, self)
        
        # NOTE: If you add any func unit, also add it in reset function and 
        # update and write function.
        self.FP_ADD = FuncUnit(2, self.CDB, 3)
        self.FP_MUL = FuncUnit(3, self.CDB, 2)
        self.BranchFU = FuncUnit(1, self.CDB, 3)
        self.Int_Calc = FuncUnit(1, self.CDB, 5)
        self.LoadStore = LoadStoreUnit(self.Memory, self.CDB, self.ROB, 4)

        # TODO: WTF is this?
        self.load_step_1_done = False

    def resetFUAndPC(self, npc):
        self.npc_line[0] = npc

        self.FP_ADD = FuncUnit(2, self.CDB, 3)
        self.FP_MUL = FuncUnit(3, self.CDB, 2)
        self.BranchFU = FuncUnit(1, self.CDB, 3)
        self.Int_Calc = FuncUnit(1, self.CDB, 5)
        self.LoadStore = LoadStoreUnit(self.Memory, self.CDB, self.ROB, 4)
        self.load_step_1_done = False

    def triggerClock(self):
        # try:
        #     print 'Printing bottom of instr queue in ExeModule', self.instr_queue[-1]
        # except:
        #     print 'Whole instr queue', self.instr_queue
        self._issue()
        self._execute()
        self._writeResult()
        self._commit()

    def _issue(self):
        if len(self.instr_queue) > 0:
            RS_success = 0
            curr_instr = self.instr_queue[0]
            temp_RS_entry = {'Busy':True, 'Vj':0, 'Vk':0, 'Qj':0, 'Qk':0, 'Dest':0, 'A':0, 'func': add}

            if self.ROB != self.ROB.tail or self.ROB.size == 0: # implies there is space in ROB

                # TODO: Where is this from?
                if curr_instr['Op'] in ['BNE', 'BEQ']:
                    self.ROB.global_spec_counter += 1
                    FU = self._setRSEntryForBranch(curr_instr, temp_RS_entry)

                elif curr_instr['Op'] in ['ADDI', 'ANDI', 'ORI', 'XORI']:
                    FU = self._setRSEntryForImm(curr_instr, temp_RS_entry)
                elif curr_instr['Op'] in ['SLL']:
                    FU = self._setRSEntryForShift(curr_instr, temp_RS_entry)
                else:
                    FU = self._setRSEntry(curr_instr, temp_RS_entry)

                temp_RS_entry['Dest'] = self.ROB.tail + 1
                    
                print "RS entry to be inserted:", temp_RS_entry
                
                # checks internally if there is space in RS or not
                RS_success = FU.insert_into_RS(temp_RS_entry) 

                if RS_success < 0:
                    print "Insert Failed :( "
                    return RS_success # return -1 if no space in RS

                self.instr_queue.pop(0)
                self.ROB.insertInstr(curr_instr)
                
            else:
                return -1       # No space in ROB
        else:
            return -2           # No instr to issue

    def _execute(self):
        print "RS Updates being called"
        self.FP_ADD.update_RS()
        self.FP_MUL.update_RS()
        self.Int_Calc.update_RS()
        self.LoadStore.update_RS()
        self.BranchFU.update_RS()

        print "CDB print"
        print self.CDB
        self.ROB.update()

        del self.CDB[:] # Just to be safe in ROB
        self.FP_ADD.execute()
        self.FP_MUL.execute()
        self.Int_Calc.execute()
        self.BranchFU.execute()
        print 'step1 value as arg', self.load_step_1_done
        self.load_step_1_done = self.LoadStore.execute(self.load_step_1_done)
        print 'step1 value returned', self.load_step_1_done

    def _writeResult(self):
        self.FP_ADD.write_data_to_CDB()
        self.FP_MUL.write_data_to_CDB()
        self.Int_Calc.write_data_to_CDB()
        self.LoadStore.write_data_to_CDB()
        self.BranchFU.write_data_to_CDB()

# Check each of the functional units, and if a result is available, write it 
# on the CDB with the ROB tag. This will inturn write it to ROB entry and 
# reservation stations.
# For STORE, we need to do some special things.
        pass

    def _commit(self):
        # TODO Branch instruction with misprediction
        self.ROB.commitInstr()

    def _setRSEntry(self, curr_instr, temp_RS_entry):
        # For loads, stores, and ALU ops
        isInstrALU = 0
        isStore = 0

        if curr_instr['Op'] in ['ADD.D', 'ADD.S', 'ADD']:
            temp_RS_entry['func'] = add
        if curr_instr['Op'] in ['SUB.D', 'SUB.S', 'SUB']:
            temp_RS_entry['func'] = sub
        if curr_instr['Op'] in ['MUL.D', 'MUL.S', 'MUL']:
            temp_RS_entry['func'] = mul
        if curr_instr['Op'] in ['DIV.D', 'DIV.S', 'DIV']:
            temp_RS_entry['func'] = div
        if curr_instr['Op'] in ['OR']:
            temp_RS_entry['func'] = or_func
        if curr_instr['Op'] in ['AND']:
            temp_RS_entry['func'] = and_func
        if curr_instr['Op'] in ['XOR']:
            temp_RS_entry['func'] = xor_func
        if curr_instr['Op'] in ['NOR']:
            temp_RS_entry['func'] = nor_func

        if curr_instr['Op'] in ['LB', 'LW', 'LD']:
            # TODO implementing LB and LW?
            RF = self.IntRegisterFile
            FU = self.LoadStore
            temp_RS_entry['func'] = is_load
            temp_RS_entry['A'] = curr_instr['Imm']
            temp_RS_entry['ROB_index'] = self.ROB.tail + 1

            RF[curr_instr['Vk']]['ROB_index'] = self.ROB.tail + 1
            RF[curr_instr['Vk']]['Busy'] = True
            #print '@@@@@@@@@', curr_instr['Vk'], self.ROB.tail
            # self.ROB.buffer[self.ROB.tail]['Dest'] = curr_instr['Vk']

            # Following lines are needed in calculating the effective address.
            first_state = RF[curr_instr['Vj']]['Busy']
            first_ROB_index = RF[curr_instr['Vj']]['ROB_index']

            if(first_state == True):
                entry = self.ROB.buffer[first_ROB_index - 1]
                #print 'entry 1 =', entry
                if entry['Ready']:
                    temp_RS_entry['Vj'] = entry['Value']
                else:
                    temp_RS_entry['Qj'] = RF[curr_instr['Vj']]['ROB_index']
            else:
                temp_RS_entry['Vj'] = RF[curr_instr['Vj']]['Value']

        elif curr_instr['Op'] in ['SW', 'SB', 'SD']:
            # TODO implementing SB and SW?
            isStore = 1
            temp_RS_entry['A'] = curr_instr['Imm']
            RF = self.IntRegisterFile
            FU = self.LoadStore

        elif curr_instr['Op'] in ['ADD.D', 'ADD.S', 'SUB.D', 'SUB.S']:
            RF = self.FPRegisterFile
            FU = self.FP_ADD
            isInstrALU = 1

        elif curr_instr['Op'] in ['MUL.D', 'MUL.S', 'DIV.D', 'DIV.S']:
            RF = self.FPRegisterFile
            FU = self.FP_MUL
            isInstrALU = 1

        elif curr_instr['Op'] in ['ADD', 'SUB', 'MUL', 'DIV', 'AND', 'OR', 'XOR', 'NOR']:
            RF = self.IntRegisterFile
            FU = self.Int_Calc
            isInstrALU = 1
        
        else:
            print "----------------------------------------------------------------------------------------------------Wut!?"
    
        if isInstrALU is 1 or isStore is 1:
            first_state = RF[curr_instr['Vj']]['Busy']
            first_ROB_index = RF[curr_instr['Vj']]['ROB_index']
            second_state = RF[curr_instr['Vk']]['Busy']
            second_ROB_index = RF[curr_instr['Vk']]['ROB_index']

            if(first_state == True):
                entry = self.ROB.buffer[first_ROB_index - 1]
                #print 'entry 1 =', entry
                if entry['Ready']:
                    temp_RS_entry['Vj'] = entry['Value']
                else:
                    temp_RS_entry['Qj'] = RF[curr_instr['Vj']]['ROB_index']
            else:
                temp_RS_entry['Vj'] = RF[curr_instr['Vj']]['Value']

            if(second_state == True):
                entry = self.ROB.buffer[second_ROB_index - 1]
                #print 'entry 2 =', entry
                print '------------ROB index--------', second_ROB_index - 1
                if entry['Ready']:
                    temp_RS_entry['Vk'] = entry['Value']
                else:
                    temp_RS_entry['Qk'] = RF[curr_instr['Vk']]['ROB_index']
            else:
                temp_RS_entry['Vk'] = RF[curr_instr['Vk']]['Value']

        # Following 2 lines not needed for Stores
        # TODO are they required for Branch? otherwise we can put them in the isInstrALU block
        if curr_instr['Op'] not in ['SW', 'SB', 'SD', 'LW', 'LB', 'LD']:
            RF[curr_instr['Dest']]['Busy'] = True
            RF[curr_instr['Dest']]['ROB_index'] = self.ROB.tail + 1

        return FU

    def _setRSEntryForImm(self, curr_instr, temp_RS_entry):
        RF = self.IntRegisterFile
        FU = self.Int_Calc

        if curr_instr['Op'] == 'ADDI':
            temp_RS_entry['func'] = add
        if curr_instr['Op'] == 'ANDI':
            temp_RS_entry['func'] = and_func
        if curr_instr['Op'] == 'ORI':
            temp_RS_entry['func'] = or_func
        if curr_instr['Op'] == 'XORI':
            temp_RS_entry['func'] = xor_func
        if curr_instr['Op'] in ['NORI']:
            temp_RS_entry['func'] = nor_func

        first_state = RF[curr_instr['Vj']]['Busy']
        first_ROB_index = RF[curr_instr['Vj']]['ROB_index']

        if(first_state == True):
            entry = self.ROB.buffer[first_ROB_index - 1]
            #print 'entry 1 =', entry
            if entry['Ready']:
                temp_RS_entry['Vj'] = entry['Value']
            else:
                temp_RS_entry['Qj'] = RF[curr_instr['Vj']]['ROB_index']
        else:
            temp_RS_entry['Vj'] = RF[curr_instr['Vj']]['Value']

        temp_RS_entry['Vk'] = curr_instr['Imm']

        RF[curr_instr['Vk']]['Busy'] = True
        RF[curr_instr['Vk']]['ROB_index'] = self.ROB.tail + 1

        return FU

    def _setRSEntryForShift(self, curr_instr, temp_RS_entry):
        RF = self.IntRegisterFile
        FU = self.Int_Calc

        if curr_instr['Op'] == 'SLL':
            temp_RS_entry['func'] = shift_left

        first_state = RF[curr_instr['Vj']]['Busy']
        first_ROB_index = RF[curr_instr['Vj']]['ROB_index']

        if(first_state == True):
            entry = self.ROB.buffer[first_ROB_index - 1]
            #print 'entry 1 =', entry
            if entry['Ready']:
                temp_RS_entry['Vj'] = entry['Value']
            else:
                temp_RS_entry['Qj'] = RF[curr_instr['Vj']]['ROB_index']
        else:
            temp_RS_entry['Vj'] = RF[curr_instr['Vj']]['Value']

        temp_RS_entry['Vk'] = curr_instr['Imm']

        RF[curr_instr['Dest']]['Busy'] = True
        RF[curr_instr['Dest']]['ROB_index'] = self.ROB.tail + 1

        return FU

    def _setRSEntryForBranch(self, curr_instr, temp_RS_entry):
        RF = self.IntRegisterFile
        FU = self.BranchFU

        if curr_instr['Op'] == 'BNE':
            temp_RS_entry['func'] = not_equal_to
        elif curr_instr['Op'] == 'BEQ':
            temp_RS_entry['func'] = equal_to

        first_state = RF[curr_instr['Vj']]['Busy']
        first_ROB_index = RF[curr_instr['Vj']]['ROB_index']
        second_state = RF[curr_instr['Vk']]['Busy']
        second_ROB_index = RF[curr_instr['Vk']]['ROB_index']

        if(first_state == True):
            entry = self.ROB.buffer[first_ROB_index - 1]
            #print 'entry 1 =', entry
            if entry['Ready']:
                temp_RS_entry['Vj'] = entry['Value']
            else:
                temp_RS_entry['Qj'] = RF[curr_instr['Vj']]['ROB_index']
        else:
            temp_RS_entry['Vj'] = RF[curr_instr['Vj']]['Value']

        if(second_state == True):
            entry = self.ROB.buffer[second_ROB_index - 1]
            #print 'entry 2 =', entry
            print '------------ROB index--------', second_ROB_index - 1
            if entry['Ready']:
                temp_RS_entry['Vk'] = entry['Value']
            else:
                temp_RS_entry['Qk'] = RF[curr_instr['Vk']]['ROB_index']
        else:
            temp_RS_entry['Vk'] = RF[curr_instr['Vk']]['Value']

        return FU
