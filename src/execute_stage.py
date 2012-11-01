from executer_buffer import ExecuterBuffer
from decoder_buffer import DecoderBuffer

class ExecuteStage(object):
    """Simulator for the Execute stage of a MIPS pipeline.
    """
    
    def __init__(self, decoder_buffer, executer_buffer, register_file):
        """Set the decoder buffer and executer buffer for the Execute Stage.
        """
        self.decoder_buffer = decoder_buffer
        self.executer_buffer = executer_buffer

        # TODO: DO NOT access register_file in any way in this stage!
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

            # TODO: THIS IS WRONG!!! Simply send the operation's
            # value. No reading of register_file here.
            self.register_file [instr.rd] = self.do_operation(
                instr.opcode,
                self.decoder_buffer.rs[1],
                self.decoder_buffer.rt[1]
                )
            self.decoder_buffer = DecoderBuffer()
            self.executer_buffer.update({
                'is_executer_stalled': is_executer_stalled,
                'instr': instr,
                'npc': npc,
                'rd': [instr.rd, self.register_file [instr.rd]],
                })
        else:
            # Here, we should take care of operand fowarding
            is_executer_stalled = True
            self.executer_buffer.update({
                'is_executer_stalled': is_executer_stalled,
                })
        
    def execute_I_instruction(self):
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
        instr = self.decoder_buffer.instr
        npc = self.decoder_buffer.npc
        is_executer_stalled = False

        # Check if operands are in the buffer.
        if (self.decoder_buffer.rs is not None and
            self.decoder_buffer.immediate is not None):
            # Immediate ALU operations
            if len (instr.opcode) == 4:
                self.register_file [instr.rt] = self.do_operation (
                    instr.opcode,
                    self.decoder_buffer ['rs'] [1],
                    self.decoder_buffer ['immediate']
                )
                self.decoder_buffer = DecoderBuffer()
                self.executer_buffer.update({
                    'is_executer_stalled': is_executer_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, self.register_file [instr.rt]]
                    })
                return

            # Load : rt <- mem [imm (rs)]
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'L'):
                memaddr = (self.decoder_buffer ['rs'] [1]
                           +
                           self.decoder_buffer ['immediate'])
                self.decoder_buffer = DecoderBuffer()

                # TODO: Why is rt here not of the form 
                # [instr.rt, self.register_file [instr.rt]] like the
                # others?
                self.executer_buffer.update({
                    'is_executer_stalled': is_executer_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': instr.rt,
                    'memaddr': memaddr
                    })
                return

            # Store: mem [imm (rs)] <- rt
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'S'):
                memaddr = (self.decoder_buffer ['rs'] [1]
                           +
                           self.decoder_buffer ['immediate'])
                self.decoder_buffer = DecoderBuffer()
                self.executer_buffer.update({
                    'is_executer_stalled': is_executer_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, self.register_file [instr.rt]],
                    'memaddr': memaddr,
                    })
                return

        else:
            is_executer_stalled = True
            self.executer_buffer.update({
                'is_executer_stalled': is_executer_stalled,
                })
            return

        # BEQ and BNE
        if (self.decoder_buffer.rs is not None and
            self.decoder_buffer.immediate is not None and
            self.decoder_buffer.rt is not None):
            condition_output = True

            if (len (instr.opcode) == 3 and
                instr.opcode == 'BEQ'):
                condition_output = (
                    self.decoder_buffer ['rs'] [1]
                    ==
                    self.decoder_buffer ['rt'] [1]
                )
            elif (len (instr.opcode) == 3 and
                instr.opcode == 'BNE'):
                condition_output = not (
                    self.decoder_buffer ['rs'] [1]
                    ==
                    self.decoder_buffer ['rt'] [1]
                )
            if condition_output:
                PC = npc + 4 * instr.immediate
                print 'BNE/BEQ: PC changed to', PC
            else:
                # TODO: Should this be npc or npc - 4?
                PC = npc

            self.decoder_buffer = DecoderBuffer()
            self.executer_buffer.update({
                'is_executer_stalled': is_executer_stalled,
                'instr': instr,
                'npc': npc,
                'PC': PC,
                })
            return
        else: 
            is_executer_stalled = True
            self.executer_buffer.update({
                'is_executer_stalled': is_executer_stalled,
                })
            return

    def execute (self, is_mem_stalled = False):
        """Execute instruction.
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
            return
        if self.decoder_buffer.instr.type == 'I':
            self.execute_I_instruction()
            return
