#!/usr/bin/env python

class RegisterFile (object):

    # R1 value 6, dirty means
    # self.regs [1] is (6, True)
    def __init__ (self):
        self.regs = {}
        for i in range (32):
            self.regs [i] = [0, False]

    def __getitem__ (self, register_number):
        return self.regs [register_number] [0]

    def __setitem__ (self, register_number, value):
        old_val, old_status = self.regs [register_number]
        return self.regs.__setitem__ (register_number,
                                      [value, old_status])

    def isDirty (self, reg_number):
        return self.regs [reg_number] [1]

    def isClean (self, reg_number):
        return not self.isDirty (reg_number)

    def setDirty (self, reg_number):
        self.regs [reg_number] [1] = True

    def setClean (self, reg_number):
        self.regs [reg_number] [1] = False

    def __str__ (self):
        str_repr = ""
        for i in range (8):
            for j in range (4):
                index = 8 * j + i
                str_repr += "R" + str (index) + " "
                str_repr += str (self [index])
                if self.isDirty (index): str_repr += " *"
                str_repr += '\t'
            str_repr += '\n'
        return str_repr

if __name__ == "__main__":
    reg_file = RegisterFile ()
    print reg_file
