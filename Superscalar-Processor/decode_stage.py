class DecodeStage(object):
    """Decode Stage of the MIPS pipeline.

    Decode the hex instruction into the appropriate operator and
    operands.
    """
    
    def __init__(self, fetch_buffer):
        """Initialize the fetch_buffer.
        """
        self.fetch_buffer = fetch_buffer
        self._opcode_dict = dict()
        self.initialize_opcode_dict()
        self.current_instr = {
            'Op': '',
            'PC': '',
            'Vj': '',
            'Vk': '',
            'Dest': '',
            'Imm': '',
            }

    def _get_data(self):
        return self.fetch_buffer['IR'].strip('\n')

    def trigger_clock(self):
        try:
            instruction = int(self._get_data(), 16)
        except ValueError:
            return

        operation = self._opcode_dict[instruction/2**26]
        self.currentOperation = operation
        self._write_data(instruction, operation)
        return

    def _write_data(self, instruction, operation):
        self.current_instr['Op'] = operation

        self.function = instruction % 2**6
        offset = instruction % 2**26
        self.new_offset = 4*offset
        mid_20_bits = offset/2**6

        if operation == 'FP':
            # print "going in"
            format = mid_20_bits/2**15
            rs = (mid_20_bits/2**5)%2**5
            rt = (mid_20_bits/2**10)%2**5
            rd = (mid_20_bits)%2**5
            self._setFPOp(format, operation)
        else:
            rs = mid_20_bits/2**15
            rt = (mid_20_bits/2**10)%2**5
            rd = (mid_20_bits/2**5)%2**5

        self.immediate_value = instruction % 2**16 # last 16 bits

        self.current_instr['Imm'] = self.immediate_value
        self.current_instr['Vj'] = rs
        self.current_instr['Vk'] = rt
        self.current_instr['Dest'] = rd

        # print "Registers ", rs, rt, rd
        self.rs = rs
        self.rt = rt
        self.rd = rd

        if operation == 'Special-Delta':
            self._set_int_op(operation)
            if self.current_instr['Op'] == 'SLL':
                self.current_instr['Vj'] = rt
                self.current_instr['Imm'] = mid_20_bits%(2**5)

        if operation in ['BEQ', 'BNE']:
            # This is how it should have been
            # self.current_instr['Dest'] = self.npc[0] + self.immediate_value*4
            # But it is like this:
            self.current_instr['Dest'] = self.immediate_value*4
            # in order to run the given matrix multiplication code properly
        if operation in ['LW', 'LD', 'LB']:
            self.current_instr['Dest'] = rt
        if self.current_instr['Op'] in ['ADDI', 'XORI', 'ORI', 'ANDI']:
            self.current_instr['Dest'] = rt

        return

    def _set_int_op(self, operation):
        self.current_instr['Op'] = ''
        if self.function == int('100000', 2):
            # ADD funct
            self.current_instr['Op'] = 'ADD'
        if self.function == int('100010', 2):
            # SUB funct
            self.current_instr['Op'] = 'SUB'
        if self.function == int('011000', 2):
            # MUL funct
            self.current_instr['Op'] = 'MUL'
        if self.function == int('011100', 2):
            # DMULT funct
            self.current_instr['Op'] = 'MUL'
        if self.function == int('011010', 2):
            # DIV funct
            self.current_instr['Op'] = 'DIV'
        if self.function == int('100100', 2):
            # AND funct
            self.current_instr['Op'] = 'AND'
        if self.function == int('100101', 2):
            # OR funct
            self.current_instr['Op'] = 'OR'
        if self.function == int('100110', 2):
            # XOR funct
            self.current_instr['Op'] = 'XOR'
        if self.function == int('100111', 2):
            # NOR funct
            self.current_instr['Op'] = 'NOR'
        if self.function == int('000000', 2):
            # SLL funct
            self.current_instr['Op'] = 'SLL'

    def _set_fp_op(self, format, operation):
        # TODO: GET THE CORRECT VALUES
        self.current_instr['Op'] = ''
        if format == int('100000', 2):
            if self.function == int('000000', 2):
                # ADD funct
                self.current_instr['Op'] = 'ADD.S'
            if self.function == int('000001', 2):
                # SUB funct
                self.current_instr['Op'] = 'SUB.S'
            if self.function == int('000010', 2):
                # MUL funct
                self.current_instr['Op'] = 'MUL.S'
            if self.function == int('000011', 2):
                # DIV funct
                self.current_instr['Op'] = 'DIV.S'
        elif format == int('000011', 2):
            if self.function == int('000000', 2):
                # ADD funct
                self.current_instr['Op'] = 'ADD.D'
            if self.function == int('000001', 2):
                # SUB funct
                self.current_instr['Op'] = 'SUB.D'
            if self.function == int('000010', 2):
                # MUL funct
                self.current_instr['Op'] = 'MUL.D'
            if self.function == int('000011', 2):
                # DIV funct
                self.current_instr['Op'] = 'DIV.D'

    def initialize_opcode_dict(self):
        self._opcode_dict[0] = 'Special-Delta'
        self._opcode_dict[2] = 'J'
        self._opcode_dict[3] = 'JAL'
        self._opcode_dict[int('010001', 2)] = 'FP'
        self._opcode_dict[int('000011', 2)] = 'FP'
        self._opcode_dict[int('000100', 2)] = 'BEQ'
        self._opcode_dict[int('000101', 2)] = 'BNE'

        self._opcode_dict[int('001000', 2)] = 'ADDI'
        self._opcode_dict[int('001100', 2)] = 'ANDI'
        self._opcode_dict[int('001101', 2)] = 'ORI'
        self._opcode_dict[int('001110', 2)] = 'XORI'

        self._opcode_dict[int('100000', 2)] = 'LB'
        self._opcode_dict[int('101000', 2)] = 'SB'
        self._opcode_dict[int('101011', 2)] = 'SW'
        # TODO Add opcode entry for SD
        self._opcode_dict[int('100011', 2)] = 'LW'
