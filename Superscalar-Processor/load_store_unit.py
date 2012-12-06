from func_unit import FuncUnit
from operations import *

class LoadStoreUnit(FuncUnit):
    """
    Simulator for a Load Store Unit.
    """

    def __init__(self, Memory, CDB, ROB, RS_max_size):
        """
        Initialize with the Memory and ROB.
        """
        super(LoadStoreUnit, self).__init__(1, CDB, RS_max_size)
        self.Memory = Memory

        # Required cos you need to check for pending Stores (in the
        # case of a Load), etc.
        self.ROB = ROB
        self.mem_value_read = 0

    def is_load_instrn(self, RS_index):
        """Return True iff instruction at RS_index is a Load.
        """
        return self.RS[RS_index]['func'] == is_load
    
    def no_stores_before_instrn_in_ROB(self, RS_index):
        """Return True iff there are no stores ahead of RS_index instruction in ROB.
        """
        errorFlag = False
        curr_ROB_entry = self.ROB.head
        for x in xrange(self.ROB.size):
            if (curr_ROB_entry + 1) != self.RS[RS_index]['ROB_index']:
                if self.ROB.buffer[curr_ROB_entry]['Instr']['Op'] in ['SW', 'SB', 'SD']:
                    print "BEWARE! errorFlag2 is being set!"
                    errorFlag = True
                    break
                curr_ROB_entry = (curr_ROB_entry + 1) % self.ROB.size
                continue
            
            # Will reach here only if no stores before
            # this Load. errorFlag will be False
            break

        if errorFlag is False:
            print "Error flag false"
        return not errorFlag

    def all_stores_ahead_have_diff_destn(self, RS_index):
        """Return True iff all stores ahead have different destinations.
        """
        errorFlag = False
        curr_ROB_entry = self.ROB.head
        while (curr_ROB_entry + 1) is not self.RS[RS_index]['ROB_index']:
            if self.ROB.buffer[curr_ROB_entry]['Instr']['Op'] in ['SW', 'SB', 'SD']:
                if self.ROB.buffer[curr_ROB_entry]['Dest'] == self.ROB.buffer[self.RS[RS_index]['ROB_index']]['Dest']:
                    print "BEWARE! errorFlag is being set!"
                    errorFlag = True
            curr_ROB_entry = curr_ROB_entry + 1 % self.ROB.size

        return not errorFlag

    def execute(self, load_step_1_done):
        """Execute the first Load or Store in the RS.

        Return True iff it was a Load and the first step was done.

        Load - Step 1: If base address val is available and no stores
        (to any destination?) are ahead in the ROB buffer, then
        compute and store Effective Address.

        Load - Step 2: If Step 1 is done and all store ahead have
        different destinations, then read from Memory[EA].

        Store: If base address is available, calculate EA.
        """ 
        for i in xrange(len(self.RS)):
            if self.is_load_instrn(i):
                # perform a load
                if not load_step_1_done:
                    # do step1 of load
                    print 'doing step1 for', self.RS[i]
                    if self.RS[i]['Qj'] == 0 and self.no_stores_before_instrn_in_ROB(i):
                        self.RS[i]['A'] = self.RS[i]['A'] + self.RS[i]['Vj']
                        load_step_1_done = True
                else:
                    print 'doing step2 for', self.RS[i]
                    # do step2 of load
                    if self.all_stores_ahead_have_diff_destn(i):
                        self.mem_value_read = self.Memory[self.RS[i]['A']]

                        # Load finished. Memory load bus not busy anymore.
                        # Ready to pop RS[i] in write_data_to_CDB function.
                        self.RS[i]['Busy'] = False      

                        load_step_1_done = False
                    
                print "Step 1 value before return", load_step_1_done
                return load_step_1_done
            else:
                # perform a store
                if self.RS[i]['Qj'] == 0:
                    self.ROB.buffer[self.RS[i]['Dest'] - 1]['Dest'] = self.RS[i]['Vj'] + self.RS[i]['A']
                
                return False

    def write_data_to_CDB(self):
        """Write result of ONE completed Load or Store into CDB.

        Remove that RS entry.
        """ 

        for i in xrange(len(self.RS)):
            if self.RS[i]['func'](0, 0) == 1:
                if self.RS[i]['Busy'] == False:
                    # do the following only for a load
                    print "LOAD happened rob index", self.RS[i]['Dest']
                    self.CDB.append([self.mem_value_read, self.RS[i]['Dest']])
                    self.RS.pop(i)
                    break

            else:
                # do the following only for a store
                if not self.is_waiting_for_val(i):
                    print "Making Value of ROB_index", self.RS[i]['Dest'], "with value", self.RS[i]['Vk']
                    self.ROB.buffer[self.RS[i]['Dest'] - 1]['Value'] = self.RS[i]['Vk']
                    self.ROB.buffer[self.RS[i]['Dest'] - 1]['Ready'] = True
                    self.RS.pop(i)
                    break
