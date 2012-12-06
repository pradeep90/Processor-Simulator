class FuncUnit(object):
    """
    Simulator for a Functional Unit.
    """

    def __init__(self, compute_latency, CDB, RS_max_size):
        """
        Initialize with FU latency and the Reservation Station's max size.
        """
        self.RS_max_size = RS_max_size
        self.RS = []
        self.op_queue = []
        self.compute_latency = compute_latency
        self.CDB = CDB

    def insert_into_RS(self, data):
        """Append a COPY of the data dict to the RS.

        Return length of RS or -1, if insertion failed.
        """
        if(len(self.RS) < self.RS_max_size):
            self.RS.append(data.copy())
            return len(self.RS)
        else:
            return -1

    def execute(self):
        """Execute (and remove) one ready instruction from RS.

        Append the in-flight instruction to op_queue, where it will
        take the appropriate latency before completing.
        """ 
        for i in xrange(len(self.RS)):
            if not self.is_waiting_for_val(i):
                self.execute_and_pop_instruction(i)
                break

    def update_RS(self):
        """Update values of RS variables from the CDB (if available).

        The latest value in CDB should be put into the waiting RS
        variable in case there are there are more than one update to
        the same register.
        """ 
        for i in xrange(len(self.RS)):
            if self.is_waiting_for_val(i):
                self.update_RS_val(i)

    def write_results_to_CDB(self):
        """Write results of completed instructions into CDB.

        Make sure that the appropriate FU latency has elapsed.
        """ 
        for i in xrange(len(self.op_queue)):
            self.update_op_queue_execution_time(i)

        cdb_bound_results = [
            [func(val1, val2), dest_reg] 
            for val1, val2, dest_reg, elapsed_time, func in self.op_queue
            if elapsed_time == self.compute_latency]

        self.op_queue = [op_elem for op_elem in self.op_queue
                         if op_elem[3] != self.compute_latency]

        self.CDB += cdb_bound_results

    def is_waiting_for_val(self, RS_index):
        """Return True iff instruction at RS[RS_index] is waiting for values.
        """
        return self.RS[RS_index]['Qj'] != 0 or self.RS[RS_index]['Qk'] != 0

    def execute_and_pop_instruction(self, RS_index):
        """Execute and place value of RS_index instruction on op_queue.
        
        Remove it from RS.
        """
        val1 = self.RS[RS_index]['Vj']
        val2 = self.RS[RS_index]['Vk']
        dest_reg = self.RS[RS_index]['Dest']
        operation = self.RS[RS_index]['func']
        self.op_queue.append([val1, val2, dest_reg, 0, operation])
        self.RS.pop(RS_index)

    def update_RS_val(self, RS_index):
        """Get latest values for instruction at RS_index from CDB (if available).
        """
        qj = self.RS[RS_index]['Qj']
        qk = self.RS[RS_index]['Qk']
        for CDB_elem in self.CDB:
            if CDB_elem[1] == qj:
                self.RS[RS_index]['Qj'] = 0
                self.RS[RS_index]['Vj'] = CDB_elem[0]
                # print 'somthing waiting on j = ', qj, ' is cleared.'
            if CDB_elem[1] == qk:
                self.RS[RS_index]['Qk'] = 0
                self.RS[RS_index]['Vk'] = CDB_elem[0]
                # print 'somthing waiting on k = ', qk, ' is cleared.'

    def update_op_queue_execution_time(self, op_queue_index):
        """Increment the execution time field for the in-flight instruction.
        """
        self.op_queue[op_queue_index][3] += 1
