import Processor

class ExecuteStage(object):
    """Simulator for the Execute stage of a MIPS pipeline.
    """
    
    def __init__(self, ):
        """
        """
        pass

    @staticmethod
    def execute_R_instruction(decoder_buffer):
        """Execute the R instruction and update the register file.

        Return mem_buffer.

        mem_buffer contains:
        + register_file
        + next decoder_buffer
        + instr
        + npc
        + is_executor_stalled
        
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
        is_executor_stalled = False

        # Check if operands are in the buffer
        if (decoder_buffer.has_key ('rs') and
            decoder_buffer.has_key ('rt')):
            register_file [instr.rd] = Processor.Processor.do_operation (
                instr.opcode,
                decoder_buffer ['rs'] [1],
                decoder_buffer ['rt'] [1]
                )
            decoder_buffer = {}
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                'instr': instr,
                'npc': npc,
                'rd': [instr.rd, register_file [instr.rd]],
                }
        else:
            # Here, we should take care of operand fowarding
            is_executor_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                }
        
    @staticmethod
    def execute_I_instruction(decoder_buffer):
        """Execute the I instruction and update the register file.

        Return mem_buffer.

        mem_buffer contains:
        + register_file
        + next decoder_buffer
        + is_executor_stalled
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
        is_executor_stalled = False

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
                    'is_executor_stalled': is_executor_stalled,
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
                    'is_executor_stalled': is_executor_stalled,
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
                    'is_executor_stalled': is_executor_stalled,
                    'instr': instr,
                    'npc': npc,
                    'rt': [instr.rt, register_file [instr.rt]],
                    'memaddr': memaddr,
                    }

        else:
            is_executor_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
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
                'is_executor_stalled': is_executor_stalled,
                'instr': instr,
                'npc': npc,
                'PC': PC,
                }
        else: 
            # TODO: Should this be set to True here?
            # is_executor_stalled = True
            return {
                'register_file': register_file,
                'decoder_buffer': decoder_buffer,
                'is_executor_stalled': is_executor_stalled,
                }

    @staticmethod
    def execute (decoder_buffer):
        """
        """
        if decoder_buffer.get('is_mem_stalled', False): 
            return {}
        if not decoder_buffer.has_key ('instr'): 
            return {}

        instr = decoder_buffer ['instr']
        executor_stalled = False

        if instr.type == 'J':
            return decoder_buffer
        if instr.type == 'R':
            return execute_R_instruction(decoder_buffer)
        if instr.type == 'I':
            return execute_I_instruction(decoder_buffer)
