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

    is_stalled = False
    
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

        Arguments:
        - `fetcher_buffer`: contains
          + instr
          + npc
        """
        instr = self.fetcher_buffer.instr
        npc = self.fetcher_buffer.npc
        self.is_stalled = False

        if (self.register_file.isClean (instr.rs) and
            self.register_file.isClean (instr.rt)):

            self.fetcher_buffer = FetcherBuffer()
            self.register_file.setDirty (instr.rd)

            self.decoder_buffer.update({
                'instr': instr,
                'rs': [instr.rs, self.register_file [instr.rs]],
                'rt': [instr.rt, self.register_file [instr.rt]],
                'npc': npc,
                })
        else:
            self.is_stalled = True
            self.register_file.setDirty (instr.rd)

    def decode_I_instruction(self):
        """Return decoder_buffer given fetcher_buffer.

        I type: rt <- rs funct imm
        I type load: rt <- mem [imm (rs)]
        I type store: mem [imm (rs)] <- rt
        I type branch: jump to imm depending on comparison of rs and rt

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
        self.is_stalled = False

        # I type: rt <- rs funct imm
        # I type load: rt <- mem [imm (rs)]
        if (instr.type == 'I' and instr.opcode in [
                'ADDI', 'ANDI', 'ORI', 'XORI', 'LB', 'LW']):
            if self.register_file.isClean (instr.rs):
                self.fetcher_buffer = FetcherBuffer()
                self.register_file.setDirty (instr.rt)
                self.decoder_buffer.update({
                    'instr': instr,
                    'rs': [instr.rs, self.register_file [instr.rs]],
                    'npc': npc,
                    'immediate': instr.immediate
                    })
            else:
                self.is_stalled = True
                self.register_file.setDirty (instr.rt)
        # I type store: mem [imm (rs)] <- rt
        # I type branch: jump to imm depending on comparison of rs and rt
        elif (instr.type == 'I' and instr.opcode in ['SB', 'BEQ', 'SW', 'BNE']):
            if (self.register_file.isClean (instr.rs) and
                self.register_file.isClean (instr.rt)):
                self.fetcher_buffer = FetcherBuffer()
                self.decoder_buffer.update({
                    'instr': instr,
                    'rs': [instr.rs, self.register_file [instr.rs]],
                    'rt': [instr.rt, self.register_file [instr.rt]],
                    'npc': npc,
                    'immediate': instr.immediate
                })
            else:
                self.is_stalled = True
        
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
        
    def decode_J_instruction(self):
        """Return decoder_buffer given fetcher_buffer.

        J type instruction

        TODO: This is only for 'J' instructions. We haven't implemented 'JAL' yet.

        decoder_buffer contains:
        + instr
        + npc
        + is_decoder_stalled

        Arguments:
        - `fetcher_buffer`: contains
          + instr
          + npc
        """
        instr = self.fetcher_buffer.instr
        npc = self.fetcher_buffer.npc
        self.is_stalled = False

        self.fetcher_buffer = FetcherBuffer()
        PC = self.get_jump_address(npc, instr)

        self.decoder_buffer.update({
            'instr': instr,
            'npc': npc,
            'PC': PC,
            })

    def decode_instruction (self, is_executer_stalled = False):
        """Decode the instr in fetcher_buffer and read from registers.

        Check for possible branch. Compute branch target address, if
        needed.

        Also, update the PC to the computed branch target.

        Return decoder_buffer.
        """
        if is_executer_stalled or self.fetcher_buffer.instr is None: 
            self.decoder_buffer = DecoderBuffer({})
            return

        if self.fetcher_buffer.instr.type == 'R':
            self.decode_R_instruction()
        elif self.fetcher_buffer.instr.type == 'I':
            self.decode_I_instruction()
        elif self.fetcher_buffer.instr.type == 'J':
            self.decode_J_instruction()
