class ROB(object):
    """Class to simulate an ROB.""" 

    def __init__(self, max_size, CDB, IntRegisterFile, Memory, executer):
        """Initialize an ROB of max_size with given references.""" 
        self.max_size = max_size
        self.CDB = CDB

        # TODO: I don't think this really makes any difference.
        # Nothing changes based on it as of now.
        self.global_spec_counter = 0
        self.executer = executer

        self.size = 0
        self.Memory = Memory 
        self.head = 0
        self.tail = 0
        self.IntRegisterFile = IntRegisterFile

        # ROB will be a list of dictionaries, each entry of which will
        # correspond to one instruction.
        # Buffer is a queue implemented in a fixed-size list.
        self.buffer = [{} for i in xrange(max_size)]
        
    def insertInstr(self, instr):
        """Insert an instruction at the tail of the ROB.

        Return the ROB index for the instruction.

        Create an ROB entry, fill data into it, and insert it into the
        ROB.

        Fields for the ROB entry:
        + 'ROB_index': ROB number of this record
        + 'Busy': ROB entry is valid and it is in use. Hence, should
        not be overwritten
        + 'Instr': is the instruction itself
        + 'Ready': can take 2 values: 0 or 1. 
            0 => Result is not ready. 
            1 => Result is ready to be committed/forwarded. 
            Commit takes care of which RegFile to write the result in
        + 'Value': gives the result of execution of this instruction; 
            It is valid only when Ready bit is 1. 
            If it is a branch instruction, we increment the global
            branch speculation variable (in Issue).
        + 'Dest': is the destination field of the instruction; 
            Register number (for Loads and ALU ops) or memory address (for
            stores) where the instruction result must be written
        """ 
        ROB_entry = {
            'ROB_index': self.tail + 1,
            'Busy': True,
            'Instr': instr.copy(),
            'Ready': False,
            'Dest': instr['Dest'],
            'Value': 0,
            'Speculation': (self.global_spec_counter > 0),
            }
        self.buffer[self.tail] = ROB_entry.copy()
        self.tail = (self.tail + 1) % self.max_size
        self.size += 1
        print "ROB entry", ROB_entry
        return ROB_entry['ROB_index']

    def commitInstr(self):
        """Perform a normal commit if the head instruction is ready. 

        Remove the corresponding entry from ROB.

        Store: Write to memory.
        FP operation: Write to FPRegisterFile.
        Branch: If predicted correctly, decrement global_spec_counter. Else, flush ROB
        Integer: Write the result back if expected to.
        """
        head_instr = self.buffer[self.head]
        next_instr = self.buffer[(self.head + 1) % self.max_size]
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
                if self.is_branch_prediction_correct():
                    self.handle_correct_prediction()
                else:
                    self.handle_wrong_prediction()
                    return
            else:
                self.handle_integer_instruction()
            print 

            # We can use this entry for newer instructions.
            head_instr['Busy'] = False
            # Update head
            self.head = (self.head + 1) % self.max_size
            self.size -= 1

        self.printROB()

    def is_branch_prediction_correct(self, ):
        """Return True if the head branch instruction was predicted correctly.
        """
        head_instr = self.buffer[self.head]
        next_instr = self.buffer[(self.head + 1) % self.max_size]
        correct_taken_prediction = (head_instr['Value'] == 1 
                                    and head_instr['Dest'] == next_instr['Instr']['PC'])
        correct_not_taken_prediction = (head_instr['Value'] == 0 
                                        and head_instr['Dest'] != next_instr['Instr']['PC'])
        return correct_taken_prediction or correct_not_taken_prediction

    def handle_correct_prediction(self, ):
        """Decrement global_spec_counter and mark operations as not speculation.
        """
        # this means branch was predicted correctly
        i = (self.head + 1) % self.max_size
        while self.buffer[i]['Instr']['Op'] in ['BNE', 'BEQ']:
            self.buffer[i]['Speculation'] = False
            i = (i + 1) % self.max_size
        self.global_spec_counter -= 1

    def handle_wrong_prediction(self, ):
        """Flush ROB and set PC to corect value.
        """
        head_instr = self.buffer[self.head]
        next_instr = self.buffer[(self.head + 1) % self.max_size]
        # FLUSH everything which means ... flush in rob and 
        #TODO
        # Set PC value to dest or pc + 4
        # Reset all the busy bits in reg_file
        i = (self.head + 1) % self.max_size
        for x in xrange(self.max_size):
            self.buffer[i]['Busy'] = False
            i = (i + 1) % self.max_size

        for reg in self.IntRegisterFile:
            reg['Busy'] = False

        # for reg in self.FPRegisterFile:
        #     reg['Busy'] = False

        self.global_spec_counter = 0
        if (head_instr['Value'] == 1 and head_instr['Dest'] != next_instr['Instr']['PC']):
            npc = head_instr['Dest']
        else:
            npc = head_instr['Instr']['PC'] + 4
        self.executer.reset_func_units_and_pc(npc)
        self.head = self.tail = self.size = 0
        self.printROB()

    def handle_integer_instruction(self, ):
        """If destination reg is expecting a value from head ROB entry, fill it.
        """
        head_instr = self.buffer[self.head]
        next_instr = self.buffer[(self.head + 1) % self.max_size]
        # Integer instruction
        #print head_instr, 'is being committed'
        if self.IntRegisterFile[head_instr['Dest']]['ROB_index'] == self.head + 1:
            # Check the destination reg's ROB_index cos it might be
            # getting its value from some newer ROB instruction
            print 'Int rf ', head_instr['Dest'], ' is set to value ',\
                             head_instr['Value'], 'becos the rf rob index is ',\
                             self.IntRegisterFile[head_instr['Dest']]['ROB_index'],\
                             ' and head index is ', (self.head + 1)
            self.IntRegisterFile[head_instr['Dest']]['Value'] = head_instr['Value']
            self.IntRegisterFile[head_instr['Dest']]['Busy'] = False

    def printROB(self):
        """Print the ROB entries.""" 
        pass
        # for entry in self.buffer:
        #     print entry

        # print

    def update(self):
        """Update all ROB entries with results from CDB.""" 
        #TODO: CHECK currect state change.
        print "ROB update called"
        for CDB_elem in self.CDB:
            index = CDB_elem[1] - 1
            if (self.buffer[index]['Busy'] == True and self.buffer[index]['Ready'] == False):
                self.buffer[index]['Ready'] = True
                self.buffer[index]['Value'] = CDB_elem[0]
                print 'Setting ROB_index ', CDB_elem[1], 'with value ' , self.buffer[index]['Value']

    def flush_ROB(self):
        """Flush the ROB.""" 
        self.buffer = []
        self.head = self.tail = 1
