#!/usr/bin/env python

from Memory import Memory

class Instruction (object):

    j_type_opcode_to_repr_map = {
        '000010' : 'J',
        '000011' : 'JAL',
        }

    i_type_opcode_to_repr_map = {
        '100000' : 'LB',
        '101000' : 'SB',
        '100011' : 'LW',
        '101011' : 'SW',

        '001000' : 'ADDI',
        '001100' : 'ANDI',
        '001101' : 'ORI',
        '001110' : 'XORI',
        '000100' : 'BEQ',
        '000101' : 'BNE',
        }

    r_type_opcode_to_repr_map = {
        '100000' : 'ADD',
        '100010' : 'SUB',
        '011000' : 'MULT',
        '011010' : 'DIV',
        '100100' : 'AND',
        '100101' : 'OR',
        '100110' : 'XOR',
        '100111' : 'NOR',
        }

    def __init__ (self, bin_instr):
        self.register = bin_instr
        self.buff = {}
        self.interpret ()

    def interpret( self ) :
        '''
        R : [   6    5  5  5   5     6  ]
            [opcode rs rt rd shamt funct]
        J : [   6          26         ]
            [opcode offset-added-to-pc]
        I : [   6    5  5    16    ]
            [opcode rs rt immediate]

        returns self

        after decoding,
        attributes like
        - type
        - rs
        - rt
        - rd
        - opcode
        - immediate
        - offset_from_pc
        '''
        i_bin = self.register

        if type (i_bin) == list :
            if i_bin [0] == 'J':
                self.type = 'J'
                self.opcode = i_bin [1]
                self.offset_from_pc = int (i_bin [2])
            elif i_bin [0] == 'I':
                self.type = 'I'
                self.opcode = i_bin [1]
                self.rs = int (i_bin [2][1:])
                self.rt = int (i_bin [3][1:])
                self.immediate = int (i_bin [4])
            elif i_bin [0] == 'R':
                self.type = 'R'
                self.opcode = i_bin [1]
                self.rs = int (i_bin [2][1:])
                self.rt = int (i_bin [3][1:])
                self.rd = int (i_bin [4][1:])
            return self

        try:
            self.type = 'J'
            self.opcode = self.j_type_opcode_to_repr_map [i_bin [:6]]
            self.offset_from_pc = int (i_bin [6:], 2)
        except:
            try:
                self.type = 'I'
                self.opcode = self.i_type_opcode_to_repr_map [i_bin [:6]]
                self.rs = int (i_bin [6:11], 2)
                self.rt = int (i_bin [11:16], 2)
                self.immediate = int (i_bin [16:], 2)
            except:
                try :
                    self.type = 'R'
                    self.opcode = self.r_type_opcode_to_repr_map [i_bin [-6:]]
                    self.rs = int (i_bin [6:11], 2)
                    self.rt = int (i_bin [11:16], 2)
                    self.rd = int (i_bin [16:21], 2)
                except :
                    print "Error in parsing instruction"
                    raise Exception('Bad instruction format - has to be 32 bits long.')

        return self

    def __str__ (self):
        if self.type == 'R':
            return ' '.join ([self.opcode,
                              'R' + str (self.rs),
                              'R' + str (self.rt),
                              'R' + str (self.rd)])
        elif self.type == "I":
            return " ".join ([self.opcode,
                              'R' + str (self.rs),
                              'R' + str (self.rt),
                              str (self.immediate)])
        elif self.type == 'J':
            return " ".join ([self.opcode,
                              str (self.offset_from_pc)])

    def __repr__ (self):
        return self.__str__ ()

    def __eq__(self, other):
        """Return True iff self and other have the same attributes.
        
        Arguments:
        - `other`:
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        """Return False iff self and other have the same attributes.
        
        Arguments:
        - `other`:
        """
        return not self.__eq__(other)



if __name__ == "__main__" :
    memory = Memory ()
    memory.loadProgram ('./Input_hex_fibonacci.txt')
    for instr in memory:
        print Instruction (instr).interpret ()
