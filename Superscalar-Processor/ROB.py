class ROB:
    def __init__(self, max_size, CDB, IntRegisterFile, Memory, executer):
        self.max_size = max_size
        self.CDB = CDB
        self.global_spec_counter = 0
        self.executer = executer

        self.size = 0
        self.Memory = Memory 
        self.head = 0
        self.tail = 0
        self.IntRegisterFile = IntRegisterFile
        self.buffer = [dict()]*max_size # ROB will be a list of dictionaries, each entry of which will correspond to one instruction
        
    def insertInstr(self, instr):
        # Simply inserts an instruction at the tail of the ROB, which is the end of the list
        # We have to create a ROB entry here, fill data into it, and insert it into the ROB
        # 'ROB_index' is the ROB number of this record
        # 'Busy' indicates that this ROB entry is valid and it is in use... hence should not be overwritten unncessarily
        # 'Instr' is the instruction itself
        # 'Ready' can take 2 values: 0 or 1. 0 => Result is not ready. 1 => Result is ready to be committed/forwarded
        # 'Dest' is the destination field of the instruction; it can hold the destination register number directly
        #     Commit takes care of which RegFile to write the result in
        # 'Value' gives the result of execution of this instruction; it is valid only when Ready bit is 1
        # If it is a branch instruction, we increment the global branch speculation variable.
        ROB_entry = {'ROB_index' : self.tail + 1, 'Busy' : True, 'Instr': instr.copy(), 'Ready' : False, 'Dest' : instr['Dest'], 'Value' : 0, 'Speculation' : (self.global_spec_counter > 0)}
        self.buffer[self.tail] = ROB_entry.copy()
        self.tail = (self.tail + 1) % self.max_size
        self.size += 1
        print "ROB entry", ROB_entry
        return ROB_entry['ROB_index']

    def commitInstr(self):
        # If the instr is ready, performs a normal commit. Removes the corresponding entry from ROB.
        head_instr = self.buffer[self.head]
        next_instr = self.buffer[(self.head + 1) % 10]
        try:
            head_instr['Ready']
        except KeyError:
            print "KeyError", 'instr is', head_instr
            return

        #print 'commit checking', head_instr 
        if head_instr['Ready']:
            #print "Ready"
            if head_instr['Instr']['Op'] in ['SW', 'SB', 'SD']:
                self.Memory[head_instr['Dest']] = head_instr['Value']

            elif head_instr['Instr']['Op'][-2:] in [".D", ".S"]: # Write to FP Reg_File
                self.FPRegisterFile[head_instr['Dest']].Value = head_instr['Value']
                self.FPRegisterFile[head_instr['Dest']].Busy = False

            elif head_instr['Instr']['Op'] in ['BNE', 'BEQ']:
                #print "Branch instruction is being committed."
                if (head_instr['Value'] == 1 and head_instr['Dest'] == next_instr['Instr']['PC'])\
                        or (head_instr['Value'] == 0 and head_instr['Dest'] != next_instr['Instr']['PC']):
                    # this means branch was predicted correctly
                    i = (self.head + 1) % 10
                    while self.buffer[i]['Instr']['Op'] in ['BNE', 'BEQ']:
                        self.buffer[i]['Speculation'] = False
                        i = (i + 1) % 10
                    self.global_spec_counter -= 1
                else:
                    # FLUSH everything which means ... flush in rob and 
                    #TODO
                    # Set PC value to dest or pc + 4
                    # Reset all the busy bits in reg_file
                    i = (self.head + 1) % 10
                    for x in xrange(self.max_size):
                        self.buffer[i]['Busy'] = False
                        i = (i + 1) % 10

                    for reg in self.IntRegisterFile:
                        reg['Busy'] = False

                    # for reg in self.FPRegisterFile:
                    #     reg['Busy'] = False

                    self.global_spec_counter = 0
                    if (head_instr['Value'] == 1 and head_instr['Dest'] != next_instr['Instr']['PC']):
                        npc = head_instr['Dest']
                    else:
                        npc = head_instr['Instr']['PC'] + 4
                    self.executer.resetFUAndPC(npc)
                    self.head = self.tail = self.size = 0
                    self.printROB()
                    return
            else:
                #print head_instr, 'is being committed'
                if self.IntRegisterFile[head_instr['Dest']]['ROB_index'] == self.head + 1:
                    print 'Int rf ', head_instr['Dest'], ' is set to value ',\
                                     head_instr['Value'], 'becos the rf rob index is ',\
                                     self.IntRegisterFile[head_instr['Dest']]['ROB_index'],\
                                     ' and head index is ', (self.head + 1)
                    self.IntRegisterFile[head_instr['Dest']]['Value'] = head_instr['Value']
                    self.IntRegisterFile[head_instr['Dest']]['Busy'] = False
                
            print 

            head_instr['Busy'] = False
            self.head = (self.head + 1) % self.max_size
            self.size -= 1

        self.printROB()

    def printROB(self):
        for entry in self.buffer:
            print entry

        print

    def update(self):
        #TODO: CHECK currect state change.
        print "ROB update called"
        for CDB_elem in self.CDB:
            index = CDB_elem[1] - 1
            if (self.buffer[index]['Busy'] == True and self.buffer[index]['Ready'] == False):
                self.buffer[index]['Ready'] = True
                self.buffer[index]['Value'] = CDB_elem[0]
                print 'Setting ROB_index ', CDB_elem[1], 'with value ' , self.buffer[index]['Value']

    def flush_ROB(self):
        self.buffer = []
        self.head = self.tail = 1
