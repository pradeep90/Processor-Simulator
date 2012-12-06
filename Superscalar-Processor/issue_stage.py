from operations import *

class IssueStage(object):
    """Issue Stage of the MIPS pipeline.
    """
    
    def __init__(self, ROB, instr_queue, IntRegisterFile, 
                 FPRegisterFile, execute_module):
        """
        """
        self.ROB = ROB
        self.instr_queue = instr_queue
        self.IntRegisterFile = IntRegisterFile
        self.FPRegisterFile = FPRegisterFile
        self.execute_module = execute_module
        
    def _issue(self):
        """Issue one instruction.

        Fill out the RS entry and issue it to the appropriate FU. 
        Also insert it into the ROB.

        Return -1 if no space in RS or ROB.
        Return -2 if no instruction in instr_queue.
        """ 
        if len(self.instr_queue) > 0:
            RS_success = 0
            curr_instr = self.instr_queue[0]
            temp_RS_entry = {
                'Busy': True,
                'Vj': 0,
                'Vk': 0,
                'Qj': 0,
                'Qk': 0,
                'Dest': 0,
                'A': 0,
                'func': add,
                }

            if self.ROB.head != self.ROB.tail or self.ROB.size == 0:
                # implies there is space in ROB
                
                # TODO: Where is this from?
                if curr_instr['Op'] in ['BNE', 'BEQ']:
                    self.ROB.global_spec_counter += 1
                    FU = self._set_rs_entry_for_branch(curr_instr, temp_RS_entry)
                elif curr_instr['Op'] in ['ADDI', 'ANDI', 'ORI', 'XORI']:
                    FU = self._set_rs_entry_for_imm(curr_instr, temp_RS_entry)
                elif curr_instr['Op'] in ['SLL']:
                    FU = self._set_rs_entry_for_shift(curr_instr, temp_RS_entry)
                else:
                    FU = self._set_rs_entry(curr_instr, temp_RS_entry)

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

    def _set_rs_entry(self, curr_instr, temp_RS_entry):
        """Set fields in RS entry for normal instruction.

        This is for loads, stores, and ALU ops.
        """ 
        isInstrALU = 0
        isStore = 0

        # TODO: if curr_instr['Op'] in [... list ...]
        # temp_RS_entry['func'] = op_dict[...]
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

            temp_RS_entry['Vj'], temp_RS_entry['Qj'] = self.get_value_or_tag(curr_instr, 'j')
        elif curr_instr['Op'] in ['SW', 'SB', 'SD']:
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
    
        # TODO:  
        if isInstrALU is 1 or isStore is 1:
            first_state = RF[curr_instr['Vj']]['Busy']
            first_ROB_index = RF[curr_instr['Vj']]['ROB_index']
            second_state = RF[curr_instr['Vk']]['Busy']
            second_ROB_index = RF[curr_instr['Vk']]['ROB_index']

            temp_RS_entry['Vj'], temp_RS_entry['Qj'] = self.get_value_or_tag(curr_instr, 'j')
            temp_RS_entry['Vk'], temp_RS_entry['Qk'] = self.get_value_or_tag(curr_instr, 'k')
        # Following 2 lines not needed for Stores
        # TODO are they required for Branch? otherwise we can put them in the isInstrALU block
        if curr_instr['Op'] not in ['SW', 'SB', 'SD', 'LW', 'LB', 'LD']:
            RF[curr_instr['Dest']]['Busy'] = True
            RF[curr_instr['Dest']]['ROB_index'] = self.ROB.tail + 1

        return FU

    def _set_rs_entry_for_imm(self, curr_instr, temp_RS_entry):
        """Set fields in RS entry for Imm instruction.

        Get value or tag for Source reg.
        Get value of Imm field directly from instruction.
        Set target reg as busy and set the ROB entry which will
        generate its value.
        """ 
        RF = self.IntRegisterFile

        # Set the func to be used
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

        temp_RS_entry['Vj'], temp_RS_entry['Qj'] = self.get_value_or_tag(curr_instr, 'j')

        temp_RS_entry['Vk'] = curr_instr['Imm']

        RF[curr_instr['Vk']]['Busy'] = True
        RF[curr_instr['Vk']]['ROB_index'] = self.ROB.tail + 1

        FU = self.Int_Calc
        return FU

    def _set_rs_entry_for_shift(self, curr_instr, temp_RS_entry):
        """Set fields in the RS entry for Shift instruction.

        Get value or tag for source reg.
        """ 
        RF = self.IntRegisterFile
        FU = self.Int_Calc

        if curr_instr['Op'] == 'SLL':
            temp_RS_entry['func'] = shift_left

        temp_RS_entry['Vj'], temp_RS_entry['Qj'] = self.get_value_or_tag(curr_instr, 'j')
        temp_RS_entry['Vk'] = curr_instr['Imm']
        RF[curr_instr['Dest']]['Busy'] = True
        RF[curr_instr['Dest']]['ROB_index'] = self.ROB.tail + 1

        return FU

    def _set_rs_entry_for_branch(self, curr_instr, temp_RS_entry):
        """Set RS entry values for branch instruction.

        Get values or tags for two operands.
        Return FuncUnit to be issued to.
        """ 
        RF = self.IntRegisterFile
        FU = self.BranchFU

        if curr_instr['Op'] == 'BNE':
            temp_RS_entry['func'] = not_equal_to
        elif curr_instr['Op'] == 'BEQ':
            temp_RS_entry['func'] = equal_to

        temp_RS_entry['Vj'], temp_RS_entry['Qj'] = self.get_value_or_tag(curr_instr, 'j')
        temp_RS_entry['Vk'], temp_RS_entry['Qk'] = self.get_value_or_tag(curr_instr, 'k')
        return FU

    def get_value_or_tag(self, curr_instr, field):
        """Get (Value, Tag) pair for field in curr_instr.

        field is 'j' or 'k'.
        """
        val_field = 'V' + field
        tag_field = 'Q' + field
        RF = self.IntRegisterFile

        first_state = RF[curr_instr[val_field]]['Busy']
        first_ROB_index = RF[curr_instr[val_field]]['ROB_index']

        if(first_state == True):
            entry = self.ROB.buffer[first_ROB_index - 1]
            #print 'entry 1 =', entry
            if entry['Ready']:
                # temp_RS_entry['Vj'] = entry['Value']
                return (entry['Value'], 0)
            else:
                # temp_RS_entry['Qj'] = RF[curr_instr['Vj']]['ROB_index']
                return (0, RF[curr_instr[val_field]]['ROB_index'])
        else:
            # temp_RS_entry['Vj'] = RF[curr_instr['Vj']]['Value']
            return (RF[curr_instr[val_field]]['Value'], 0)
