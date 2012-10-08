#!/usr/bin/env python

class Memory (object):
    '''In Memory, each instruction is stored in its binary string format.
    '''

    def __init__ (self):
        self.list = []

    def __getitem__ (self, memory_addr):
        return self.list [memory_addr / 4]

    def __setitem__ (self, memory_addr, value):
        return self.list.__setitem__ (memory_addr / 4,
                                      value)

    def __iter__ (self):
        return self.list.__iter__ ()

    def __next__ (self):
        return self.list.__next__ ()

    def __len__ (self):
        return self.list.__len__ ()

    def loadProgram (self, program_filename):
        '''Reads a file containing the MIPS code (in hex)
        and loads it into the memory, which can be accessed later. '''
        program_file = open (program_filename)
        lines = program_file.readlines ()
        program_file.close ()
        self.list = [bin (int (line, 16)) [2:].zfill (32)
                     for line in lines
                     if line.strip ()]

    def loadProgramDebug (self, program_filename):
        program_file = open (program_filename)
        text = program_file.read ()
        program_file.close ()
        self.loadProgramDebugFromText (text)

    def loadProgramDebugFromText (self, text):
        lines = text.split ('\n')
        self.list = [line.strip ().split ()
                     for line in lines
                     if line.strip ()]
        

    def __str__ (self):
        return '\n'.join (self.list)

        

if __name__ == "__main__":
    memory = Memory ()
    memory.loadProgram ('./Input_hex_fibonacci.txt')
    print memory
