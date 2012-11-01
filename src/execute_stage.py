from executer_buffer import ExecuterBuffer

class ExecuteStage(object):
    """Simulator for the Execute stage of a MIPS pipeline.
    """
    
    def __init__(self, decoder_buffer, executer_buffer, register_file):
        """Set the decoder buffer and executer buffer for the Execute Stage.
        """
        self.decoder_buffer = decoder_buffer
        self.executer_buffer = executer_buffer
        self.register_file = register_file

    @staticmethod
    def do_operation (opcode, oper1, oper2):
        """Return value of arithmetic expression `oper1 opcode oper2`.
        """
        oper_dict = {
            'ADD' : ' +',
            'ADDI': ' +',
            'SUB' : ' -',
            'MUL' : ' *',
            'DIV' : ' /',
            'AND' : ' &',
            'ANDI': ' &',
            'OR'  : ' |',
            'ORI' : ' |',
            'XOR' : ' ^',
            'XORI': ' ^',
            'NOR' : '~|',
        }
        opr = oper_dict [opcode]
        expr = (opr [0] + '('
                + str (oper1) + opr [1] + str (oper2)
                + ')')
        return eval (expr)

    def execute_R_instruction(self):
        """Execute the R instruction and update the register file.

        Return executer_buffer.

        executer_buffer contains:
        + instr
        + npc
        + is_executer_stalled
        
        Arguments:
        - `decoder_buffer`:
          + instr
          + npc
          + is_mem_stalled
        """
        instr = self.decoder_buffer.instr
        npc = self.decoder_buffer.npc
        is_executer_stalled = False

        # Check if operands are in the buffer
        if (self.decoder_buffer.rs is not None and
            self.decoder_buffer.rt is not None):
            self.register_file [instr.rd] = self.do_operation (
                instr.opcode,
                self.decoder_buffer ['rs'] [1],
                self.decoder_buffer ['rt'] [1]
                )
            self.decoder_buffer = {}
            return {
                'decoder_buffer': self.decoder_buffer,
                'is_executer_stalled': is_executer_stalled,
                'instr': instr,
                'npc': npc,
                'rd': [instr.rd, self.register_file [instr.rd]],
                }
        else:
            # Here, we should take care of operand fowarding
            is_executer_stalled = True
            return {
                'register_file': self.register_file,
                'decoder_buffer': self.decoder_buffer,
                'is_executer_stalled': is_executer_stalled,
                }
        
    @staticmethod
    def execute_I_instruction(decoder_buffer):
        """Execute the I instruction and update the register file.

        Return executer_buffer.

        executer_buffer contains:
        + register_file
        + next decoder_buffer
        + is_executer_stalled
        + instr
        + npc
        + rt
        + memaddr (optional)
        
        Arguments:
        - `decoder_buffer`:
          + instr
          + npc
          + register_file
          + is_mem_stalled
        """
        instr = decoder_buffer['instr']
        register_file = decoder_buffer['register_file']
        npc = decoder_buffer['npc']
        is_executer_stalled = False

        # Check if operands are in the buffer.
        if (decoder_buffer.has_key ('rs') and
            decoder_buffer.has_key ('immediate')):
            # Immediate ALU operations
            if len (instr.opcode) == 4:
                register_file [instr.rt] = self.do_operation (
                    instr.opcode,
                    decoder_buffer ['rs'] [1],
                    decoder_buffer ['immediate']
                )
                decoder_buffer = {}
                return {
                    'register_file': register_file,
                    'decoder_buffer': decoder_buffer,
                    'is_executer_stalled': is_executer_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, register_file [instr.rt]]
                    }

            # Load : rt <- mem [imm (rs)]
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'L'):
                memaddr = (decoder_buffer ['rs'] [1]
                           +
                           decoder_buffer ['immediate'])
                decoder_buffer = {}
                return {
                    'register_file': register_file,
                    'decoder_buffer': decoder_buffer,
                    'is_executer_stalled': is_executer_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': instr.rt,
                    'memaddr': memaddr
                    }

            # Store: mem [imm (rs)] <- rt
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'S'):
                memaddr = (decoder_buffer ['rs'] [1]
                           +
                           decoder_buffer ['immediate'])
                decoder_buffer = {}
                return {
                    'register_file': register_file,
                    'decoder_buffer': decoder_buffer,
                    'is_executer_stalled': is_executer_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, register_file [instr.rt]],
                    'memaddr': memaddr,
                    }

        else:
            is_executer_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executer_stalled': is_executer_stalled,
                }

        # BEQ and BNE
        if (decoder_buffer.has_key ('rs') and
            decoder_buffer.has_key ('immediate') and
            decoder_buffer.has_key ('rt')):
            condition_output = True
            if (len (instr.opcode) == 3 and
                instr.opcode == 'BEQ'):
                condition_output = (
                    decoder_buffer ['rs'] [1]
                    ==
                    decoder_buffer ['rt'] [1]
                )
            elif (len (instr.opcode) == 3 and
                instr.opcode == 'BNE'):
                condition_output = not (
                    decoder_buffer ['rs'] [1]
                    ==
                    decoder_buffer ['rt'] [1]
                )
            decoder_buffer = {}
            if condition_output:
                PC = npc + 4 * instr.immediate
                print 'BNE/BEQ: PC changed to', PC
            else:
                # TODO
                PC = npc

            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executer_stalled': is_executer_stalled,
                'instr': instr,
                'npc': npc,
                'PC': PC,
                }
        else: 
            # TODO: Should this be set to True here?
            # is_executer_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executer_stalled': is_executer_stalled,
                }

    def execute (self, is_mem_stalled = False):
        """
        """
        if is_mem_stalled or self.decoder_buffer.instr is None: 
            self.executer_buffer = ExecuterBuffer()
            return

        if self.decoder_buffer.instr.type == 'J':
            # TODO
            # self.executer_buffer = self.
            pass
        if self.decoder_buffer.instr.type == 'R':
            self.execute_R_instruction()
        if instr.type == 'I':
            self.execute_I_instruction()
