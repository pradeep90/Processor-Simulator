class LoadStoreUnit:
    def __init__(self, Memory, CDB, ROB, RS_max_size):
        self.RS_max_size = RS_max_size
        self.RS = []
        self.compute_latency = 1
        self.Memory = Memory
        self.CDB = CDB
        self.ROB = ROB
        self.mem_value_read = 0

    def insertIntoRS(self, data):
        if(len(self.RS) < self.RS_max_size):
            # TODO: MAY be change this.
            temp = dict()
            for key in data:
                temp[key] = data[key] 
            self.RS.append(temp)
            return len(self.RS)
        else:
            return -1

    def updateRS(self):
        for i in xrange(len(self.RS)):
            qj = self.RS[i]['Qj']
            qk = self.RS[i]['Qk']
            if(qj != 0 or qk != 0):
                for CDB_elem in self.CDB:
                    if CDB_elem[1] == qj:
                        self.RS[i]['Qj'] = 0
                        self.RS[i]['Vj'] = CDB_elem[0]
                        print 'somthing waiting on j = ', qj, ' is cleared.'
                    if CDB_elem[1] == qk:
                        self.RS[i]['Qk'] = 0
                        self.RS[i]['Vk'] = CDB_elem[0]
                        print 'somthing waiting on k = ', qk, ' is cleared.'

    def execute(self, step1done):
        for i in xrange(len(self.RS)):
            if self.RS[i]['CompFunc'](0, 0) == 1:
                # perform a load
                if step1done is True:
                    print 'doing step2 for', self.RS[i]
                    # do step2 of load
                    errorFlag = False
                    curr_ROB_entry = self.ROB.head
                    while (curr_ROB_entry + 1) is not self.RS[i]['ROB_index']:
                        if self.ROB.buffer[curr_ROB_entry]['Instr']['Op'] in ['SW', 'SB', 'SD']:
                            if self.ROB.buffer[curr_ROB_entry]['Dest'] == self.ROB.buffer[self.RS[i]['ROB_index']]['Dest']:
                                print "BEWARE! errorFlag is being set!"
                                errorFlag = True
                        curr_ROB_entry = curr_ROB_entry + 1 % self.ROB.size

                    if errorFlag is False:
                        self.mem_value_read = self.Memory[self.RS[i]['A']]

                        # Load finished. Memory load bus not busy anymore.
                        # Ready to pop RS[i] in writeDataToCDB function.
                        self.RS[i]['Busy'] = False      

                        step1done = False
                    
                else:
                    # do step1 of load
                    print 'doing step1 for', self.RS[i]
                    if self.RS[i]['Qj'] == 0:
                        errorFlag = False
                        curr_ROB_entry = self.ROB.head
                        for x in xrange(self.ROB.size):
                            if (curr_ROB_entry + 1) != self.RS[i]['ROB_index']:
                                if self.ROB.buffer[curr_ROB_entry]['Instr']['Op'] in ['SW', 'SB', 'SD']:
                                    print "BEWARE! errorFlag2 is being set!"
                                    errorFlag = True
                                    break
                                curr_ROB_entry = (curr_ROB_entry + 1) % self.ROB.size
                                continue
                            break

                        if errorFlag is False:
                            print "Error flag false"
                            self.RS[i]['A'] = self.RS[i]['A'] + self.RS[i]['Vj']
                            step1done = True

                print "Step 1 value before return", step1done
                return step1done
                
            else:
                # perform a store
                if self.RS[i]['Qj'] == 0:
                    self.ROB.buffer[self.RS[i]['Dest'] - 1]['Dest'] = self.RS[i]['Vj'] + self.RS[i]['A']
                
                return False

    def writeDataToCDB(self):
        for i in xrange(len(self.RS)):
            if self.RS[i]['CompFunc'](0, 0) == 1:
                if self.RS[i]['Busy'] == False:
                    # do the following only for a load
                    print "LOAD happened rob index", self.RS[i]['Dest']
                    self.CDB.append([self.mem_value_read, self.RS[i]['Dest']])
                    self.RS.pop(i)
                    break

            else:
                # do the following only for a store
                if(self.RS[i]['Qk'] == 0 and self.RS[i]['Qj'] == 0):
                    print "Making Value of ROB_index", self.RS[i]['Dest'], "with value", self.RS[i]['Vk']
                    self.ROB.buffer[self.RS[i]['Dest'] - 1]['Value'] = self.RS[i]['Vk']
                    self.ROB.buffer[self.RS[i]['Dest'] - 1]['Ready'] = True
                    self.RS.pop(i)
                    break
