from executer_buffer import ExecuterBuffer
from decoder_buffer import DecoderBuffer
from pipeline_stage import PipelineStage

class ExecuteStage(PipelineStage):
    """Simulator for the Execute stage of a MIPS pipeline.
    """
    branch_pc = None
    
    def __init__(self, decoder_buffer, executer_buffer):
        """Set the decoder buffer and executer buffer for the Execute Stage.
        """
        self.decoder_buffer = decoder_buffer
        self.executer_buffer = executer_buffer

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
        """Execute the R instruction and update executer_buffer and decoder_buffer.
        """
        instr = self.decoder_buffer.instr
        npc = self.decoder_buffer.npc
        self.unstall()

        # Check if operand values are in the buffer
        if (self.decoder_buffer.rs[1] is not None and
            self.decoder_buffer.rt[1] is not None):
            self.executer_buffer.update({
                'instr': instr,
                'npc': npc,
                'rd': [instr.rd, self.do_operation(instr.opcode,
                                                   self.decoder_buffer.rs[1],
                                                   self.decoder_buffer.rt[1])],
                })
            self.decoder_buffer.clear()
        else:
            print 'execute_R_instruction stall'
            print 'self.decoder_buffer: ', self.decoder_buffer
            # Here, we should take care of operand fowarding
            self.stall()
        
    def execute_I_instruction(self):
        """Execute the I instruction and update executer_buffer and decoder_buffer.
        """
        instr = self.decoder_buffer.instr
        npc = self.decoder_buffer.npc
        self.unstall()

        # Check if operand values are in the buffer.
        if (self.decoder_buffer.rs[1] is not None and
            self.decoder_buffer.immediate is not None):
            # Immediate ALU operations
            if len (instr.opcode) == 4:
                self.executer_buffer.update({
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, 
                           self.do_operation(instr.opcode,
                                             self.decoder_buffer['rs'] [1],
                                             self.decoder_buffer['immediate'])]
                    })
                self.decoder_buffer.clear()
                return

            # Load : rt <- mem [imm (rs)]
            if (len (instr.opcode) == 2 and
                instr.opcode [0] in 'L'):
                memaddr = (self.decoder_buffer ['rs'] [1]
                           +
                           self.decoder_buffer ['immediate'])
                self.decoder_buffer.clear()

                # TODO: Why is rt here not of the form 
                # [instr.rt, register value] like the
                # others?
                self.executer_buffer.update({
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
                self.executer_buffer.update({
                    'instr': instr,
                    'npc': npc,
                    'rt': self.decoder_buffer.rt,
                    'memaddr': memaddr,
                    })
                self.decoder_buffer.clear()
                return

        else:
            self.stall()
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

            self.decoder_buffer.clear()

            self.branch_pc = PC

            # self.executer_buffer.clear()
            return
        else: 
            self.stall()
            return

    def execute (self, is_mem_stalled = False):
        """Execute instruction.
        """
        self.branch_pc = None

        if is_mem_stalled or self.decoder_buffer.instr is None: 
            # self.executer_buffer.clear()
            print 'Execute - nothing happened'
            return

        if self.decoder_buffer.instr.type == 'J':
            # TODO
            # self.executer_buffer = self.
            return
        if self.decoder_buffer.instr.type == 'R':
            self.execute_R_instruction()
            return
        if self.decoder_buffer.instr.type == 'I':
            self.execute_I_instruction()
            return
