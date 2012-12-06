from RegFile import RegFile
from IFModule import IFModule

class IDModule:
    Instructions = ['0x0c100022', '0x0c10002c', '0x00044021', '0x0c100022']

    def __init__(self, predecessor, register_file):
        self.write_buffer = dict()
        self._opcode_dict = dict()
        self.getData = self.numGenerator(4)
        self.predecessor_module = predecessor

        self.initializeOpcodeDict()
        self.initializeWriteBuffer()
        self.setControls()
        self.reg_file = register_file
        self.currentOperation = ''
        self.function = 0
        self.branch = False

    def initializeWriteBuffer(self):
        self.write_buffer['rs'] = 0
        self.write_buffer['rt'] = 0
        self.write_buffer['rd'] = 0
        self.write_buffer['operation'] = ''
        self.write_buffer['ALUSrc'] = '000'
        self.write_buffer['ALUOp'] = 0
        self.write_buffer['Branch'] = 0
        self.write_buffer['MemRead'] = 0
        self.write_buffer['MemWrite'] = 0
        self.write_buffer['WB'] = 0
        self.write_buffer['RegDest'] = 0
        self.write_buffer['imm'] = 0
        self.write_buffer['npc'] = 0

    def initializeOpcodeDict(self):
        self._opcode_dict[0] = 'Special-Delta'
        self._opcode_dict[2] = 'J'
        self._opcode_dict[3] = 'JAL'
        
        self._opcode_dict[int('000100', 2)] = 'BEQ'
        self._opcode_dict[int('000101', 2)] = 'BNE'

        self._opcode_dict[int('001000', 2)] = 'ADDI'
        self._opcode_dict[int('001100', 2)] = 'ANDI'
        self._opcode_dict[int('001101', 2)] = 'ORI'
        self._opcode_dict[int('001110', 2)] = 'XORI'

        self._opcode_dict[int('100000', 2)] = 'LB'
        self._opcode_dict[int('101000', 2)] = 'SB'
        self._opcode_dict[int('100011', 2)] = 'LW'
        self._opcode_dict[int('101011', 2)] = 'SW'

    def setControls(self):
        self.controls = { 'Special-Delta'   : self.specialDelta,
                          'J'               : self.j,
                          'JAL'             : self.j,
                          'SW'              : self.sw,
                          'LW'              : self.lw,
                          'BEQ'             : self.immediate,
                          'BNE'             : self.immediate,
                          'ADDI'            : self.immediate,
                          'ANDI'            : self.immediate,
                          'ORI'             : self.immediate,
                          'XORI'            : self.immediate,
                          'ADDIU'           : self.immediate }


    def numGenerator(self, n):
        for i in xrange(n):
            yield i

    def triggerClock(self):
        self.return_value = 0
        self._decodeInstr()

    def roll_back(self):
        pass
    
    def _getData(self):
        # assuming we get big endian 
        return self.predecessor_module.write_buffer['IR'].strip('\n')

    def _decodeInstr(self):
        # In all this ... at any point, you may have to rollback.
        # So, if needed, keep the instruction of the previous thing safe.

        # Get the instruction from the IFModule.
        try:
            instruction = int(self._getData(), 16)
        except ValueError:
            return

        print hex(instruction), bin(instruction)
        operation = self._opcode_dict[instruction/2**26]
        self.currentOperation = operation
        self._writeData(instruction, operation)

    def _writeData(self, instruction, operation):
        # TODO Write index of register in RF that needs to be checked for validity... 
        # In EXE, I will do if RF[reg_addr][1] 
        # I should get data A, B, sl, imm, reg_addr, rt, rd, npc
        # and control bits WB, ALUOp, ALUSrc, MemRead in Exe stage
        # print operation,' was given'
        self.function = instruction%64
        offset = instruction%2**26
        self.new_offset = 4*offset
        mid_20_bits = offset/2**6
        rs = mid_20_bits/2**15
        rt = (mid_20_bits/2**10)%2**5
        rd = (mid_20_bits/2**5)%2**5
        self.immediate_value = instruction%2**16
        self.write_buffer['npc'] = self.predecessor_module.write_buffer['npc']
        self.write_buffer['imm'] = self.immediate_value
        self.write_buffer['rs'] = rs
        self.write_buffer['rt'] = rt
        self.write_buffer['rd'] = rd
        print "Registers ", rs, rt, rd
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.write_buffer['operation'] = operation

        print "self.branch value:", self.branch

        if self.branch == True:
            self.controls['J']
        else :
            self.controls[operation]()
        return self.return_value

    def specialDelta(self):
        self.write_buffer['MemRead'] = 0
        self.write_buffer['MemWrite'] = 0

        self.write_buffer['ALUSrc'] = '100'
        self.write_buffer['WB'] = 2
        self.write_buffer['RegDest'] = True

        if self.rs == self.rd or self.rt == self.rd:
            self.write_buffer['blah'] = True
        else :
            self.reg_file.registers[self.rd][1] = False

        if self.function == int('100000', 2):
            # ADD funct
            self.write_buffer['ALUOp'] = 0
        if self.function == int('100010', 2):
            # SUB funct
            self.write_buffer['ALUOp'] = 1
        if self.function == int('011000', 2):
            # MUL funct
            self.write_buffer['ALUOp'] = 2
        if self.function == int('011010', 2):
            # DIV funct
            self.write_buffer['ALUOp'] = 3
        if self.function == int('100100', 2):
            # AND funct
            self.write_buffer['ALUOp'] = 4
        if self.function == int('100101', 2):
            # OR funct
            self.write_buffer['ALUOp'] = 5
        if self.function == int('100110', 2):
            # XOR funct
            self.write_buffer['ALUOp'] = 6
        if self.function == int('100111', 2):
            # NOR funct
            self.write_buffer['ALUOp'] = 7

    def sw(self):
        self.write_buffer['MemRead'] = 0
        self.write_buffer['MemWrite'] = 1

        self.write_buffer['ALUSrc'] = '111'
        self.write_buffer['WB'] = 0
        self.write_buffer['RegDest'] = False

    def lw(self):
        self.write_buffer['MemRead'] = 1
        self.write_buffer['MemWrite'] = 0

        self.write_buffer['ALUSrc'] = '111'
        self.write_buffer['WB'] = 3
        self.write_buffer['RegDest'] = False

    def j(self):
        self.write_buffer['MemRead'] = 0
        self.write_buffer['MemWrite'] = 0

        self.write_buffer['ALUSrc'] = '000'
        self.write_buffer['WB'] = 0
        self.write_buffer['RegDest'] = False
        print "Setting", self.new_offset
        self.predecessor_module.J_value = self.new_offset

    def immediate(self):
        self.write_buffer['MemRead'] = 0
        self.write_buffer['MemWrite'] = 0

        self.write_buffer['RegDest'] = 0
        self.write_buffer['ALUSrc'] = '111'
        self.write_buffer['validBit'] = True
        self.write_buffer['RegDest'] = False

        operation = self.currentOperation

        if operation == 'SW' :
            self.write_buffer['ALUOp'] = -1
        if operation == 'LW':
            self.write_buffer['ALUOp'] = -1
        if operation == 'BEQ':
            self.write_buffer['ALUOp'] = 8
            self.write_buffer['ALUSrc'] = '111'
        if operation == 'BNE':
            self.write_buffer['ALUOp'] = 9
            self.write_buffer['ALUSrc'] = '111'

        if operation == 'ADDI':
            self.write_buffer['ALUOp'] = 0
            if self.rt == self.rs:
                self.write_buffer['blah'] = True
            else :
                self.reg_file.registers[self.rt][1] = False
        if operation == 'ANDI':
            self.write_buffer['ALUOp'] = 4
            if self.rt == self.rs:
                self.write_buffer['blah'] = True
            else :
                self.reg_file[self.rt][1] = False
        if operation == 'ORI':
            self.write_buffer['ALUOp'] = 5
            if self.rt == self.rs:
                self.write_buffer['blah'] = True
            else :
                self.reg_file.registers[self.rt][1] = False
        if operation == 'XORI':
            self.write_buffer['ALUOp'] = 6
            if self.rt == self.rs:
                self.write_buffer['blah'] = True
            else :
                self.reg_file.registers[self.rt][1] = False

        if operation == 'LB':
            self.write_buffer['ALUOp'] = -1
        if operation == 'SB':
            self.write_buffer['ALUOp'] = -1

def main():
    reg_file = RegFile()
    hex_code_file = file('sample_Code/Input_hex_fibonacci.txt', 'r')
    instr_cache = hex_code_file.readlines()
    fetcher = IFModule(0, instr_cache)
    decoder = IDModule(fetcher, reg_file)
    for i in xrange(10):
        reg_file.refresh()
        fetcher.triggerClock()
        decoder.triggerClock()

if __name__ == "__main__":
    main()
