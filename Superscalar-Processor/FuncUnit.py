class FuncUnit:
    def __init__(self, compute_latency, CDB, RS_max_size):
        self.RS_max_size = RS_max_size
        self.RS = []
        self.op_queue = []
        self.compute_latency = compute_latency
        self.CDB = CDB

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

    def execute(self):
        for i in xrange(len(self.RS)):
            if(self.RS[i]['Qj'] == 0 and self.RS[i]['Qk'] == 0):
                first_oprnd = self.RS[i]['Vj']
                second_oprnd = self.RS[i]['Vk']
                dest = self.RS[i]['Dest']
                operation = self.RS[i]['CompFunc']
                self.op_queue.append([first_oprnd,\
                                     second_oprnd,\
                                     dest,\
                                     0,\
                                     operation])
                self.RS.pop(i)
                break

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

    def writeDataToCDB(self):
        to_be_deleted = []
        for i in xrange(len(self.op_queue)):
            self.op_queue[i][3] += 1
            if(self.op_queue[i][3] == self.compute_latency):
                to_be_deleted.append(i)
                print 'Doing some operation on ', self.op_queue[i][0],\
                        self.op_queue[i][1], 'to get ',\
                        self.op_queue[i][4](self.op_queue[i][0],\
                                            self.op_queue[i][1]),\
                        ' and placing it on CDB with ROB_index ',\
                        self.op_queue[i][2]
                self.CDB.append([self.op_queue[i][4](self.op_queue[i][0], self.op_queue[i][1]),\
                                     self.op_queue[i][2]])

        to_be_deleted.reverse()
        for index in to_be_deleted:
            self.op_queue.pop(index)

        
