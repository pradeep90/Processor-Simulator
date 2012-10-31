from Instruction import Instruction
from Memory import Memory
from RegisterFile import RegisterFile
from pprint import pprint
from fetcher_buffer import FetcherBuffer
from decoder_buffer import DecoderBuffer
from fetch_stage import FetchStage

class DecodeStage(object):
    """Simulator for the Decode stage of a MIPS pipeline.
    """
    
    def __init__(self, fetcher_buffer, decoder_buffer, register_file):
        """Set the fetcher_buffer and decoder_buffer for the stage.
        """
        self.fetcher_buffer = fetcher_buffer
        self.decoder_buffer = decoder_buffer
        self.register_file = register_file
        
    def decode_R_instruction(self):
        """Return decoder_buffer given fetcher_buffer.

        R type: rd <- rs funct rt
        If applicable, mark the output register in the registerfile
        as dirty. And if the input registers are not dirty, then put
        them in the buffer.

        decoder_buffer contains:
        + instr
        + rs
        + rt
        + npc
        + is_decoder_stalled

        Arguments:
        - `fetcher_buffer`: contains
          + instr
          + npc
        """
        instr = self.fetcher_buffer.instr
        npc = self.fetcher_buffer.npc
        is_decoder_stalled = False

        if (self.register_file.isClean (instr.rs) and
            self.register_file.isClean (instr.rt)):

            fetcher_buffer = {}
            self.register_file.setDirty (instr.rd)

            self.decoder_buffer.update({
                'is_decoder_stalled': is_decoder_stalled,
                'instr': instr,
                'rs': [instr.rs, self.register_file [instr.rs]],
                'rt': [instr.rt, self.register_file [instr.rt]],
                'npc': npc,
                })
        else:
            is_decoder_stalled = True
            self.register_file.setDirty (instr.rd)
            self.decoder_buffer.update({
                'is_decoder_stalled': is_decoder_stalled,
            })

    def decode_I_instruction(self):
        """Return decoder_buffer given fetcher_buffer.

        I type: rt <- rs funct imm
        I type load: rt <- mem [imm (rs)]
        I type store: mem [imm (rs)] <- rt
        I type branch: jump to imm depending on comparison of rs and rt

        decoder_buffer contains:
        + modified register_file
        + next fetcher_buffer
        + instr
        + rs
        + rt
        + npc
        + is_decoder_stalled

        Arguments:
        - `fetcher_buffer`: contains
          + register_file
          + instr
          + npc
        """
        instr = fetcher_buffer.instr
        npc = fetcher_buffer.npc
        is_decoder_stalled = False

        # I type: rt <- rs funct imm
        # I type load: rt <- mem [imm (rs)]
        if (instr.type == 'I' and instr.opcode in [
                'ADDI', 'ANDI', 'ORI', 'XORI', 'LB', 'LW']):
            if register_file.isClean (instr.rs):
                fetcher_buffer = {}
                register_file.setDirty (instr.rt)
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                    'instr': instr,
                    'rs': [instr.rs, register_file [instr.rs]],
                    'npc': npc,
                    'immediate': instr.immediate
                    }
            else:
                is_decoder_stalled = True
                register_file.setDirty (instr.rt)
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                    }

        # I type store: mem [imm (rs)] <- rt
        # I type branch: jump to imm depending on comparison of rs and rt
        elif (instr.type == 'I' and instr.opcode in ['SB', 'BEQ', 'SW', 'BNE']):
            if (register_file.isClean (instr.rs) and
                register_file.isClean (instr.rt)):
                fetcher_buffer = {}
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                    'instr': instr,
                    'rs': [instr.rs, register_file [instr.rs]],
                    'rt': [instr.rt, register_file [instr.rt]],
                    'npc': npc,
                    'immediate': instr.immediate
                }
            else:
                is_decoder_stalled = True
                return {
                    'register_file': register_file,
                    'fetcher_buffer': fetcher_buffer,
                    'is_decoder_stalled': is_decoder_stalled,
                }
        
    @staticmethod
    def get_jump_address(npc, instr):
        """Return jump address for instr given npc.

        Take 4 msb of old PC
        Mul offset_from_pc by 4
        Concatenate
        That's where we should jump

        Arguments:
        - `instr`: J-type instruction.
        """
        old_pc = npc - 4
        pc_msb = Memory.get_binary_string(old_pc)[:4]
        imm = Memory.get_binary_string(instr.offset_from_pc * 4, 28)
        jump_addr = int (pc_msb + imm, 2)
        return jump_addr
        
    @staticmethod
    def decode_J_instruction(fetcher_buffer):
        """Return decoder_buffer given fetcher_buffer.

        J type instruction

        decoder_buffer contains:
        + register_file
        + next fetcher_buffer
        + instr
        + npc
        + is_decoder_stalled

        Arguments:
        - `fetcher_buffer`: contains
          + register_file
          + instr
          + npc
        """
        register_file = fetcher_buffer['register_file']
        instr = fetcher_buffer ['instr']
        npc = fetcher_buffer ['npc']
        is_decoder_stalled = False

        fetcher_buffer = {}
        PC = DecodeStage.get_jump_address(npc, instr)
        print 'npc: ', npc
        print 'jump_addr: ', PC

        return {
            'register_file': register_file,
            'fetcher_buffer': fetcher_buffer,
            'is_decoder_stalled': is_decoder_stalled,
            'instr': instr,
            'npc': npc,
            'PC': PC,
            }

    def decode_instruction (self, is_executor_stalled = False):
        """Decode the instr in fetcher_buffer and read from registers.

        Check for possible branch. Compute branch target address, if
        needed.

        Also, update the PC to the computed branch target.

        Return decoder_buffer.
        """
        if is_executor_stalled or self.fetcher_buffer.instr is None: 
            self.decoder_buffer = DecoderBuffer({})
            return

        if self.fetcher_buffer.instr.type == 'R':
            return self.decode_R_instruction()
        elif self.fetcher_buffer.instr.type == 'I':
            return self.decode_I_instruction()
        elif self.fetcher_buffer.instr.type == 'J':
            return self.decode_J_instruction()
