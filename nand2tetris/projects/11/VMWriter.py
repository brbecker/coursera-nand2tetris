class VMWriter():
    '''
    Emits VM commands into a file, using the VM command syntax.
    '''

    def __init__(self, vmFile, DEBUG=False):
        '''
        Creates a new file and prepares it for writing.
        '''
        pass
    
    def writePush(self, segment, index):
        '''
        Writes a VM push command.
        '''
        pass
    
    def writePop(self, segment, index):
        '''
        Writes a VM pop command.
        '''
        pass
    
    def writeArithmetic(self, command):
        '''
        Writes a VM arithmetic command.
        '''
        pass
    
    def writeLabel(self, label):
        '''
        Writes a VM label command.
        '''
        pass
    
    def writeGoto(self, label):
        '''
        Writes a VM goto command.
        '''
        pass
    
    def writeIf(self, label):
        '''
        Writes a VM if-goto command.
        '''
        pass
    
    def writeCall(self, name, nArgs):
        '''
        Writes a VM call command.
        '''
        pass
    
    def writeFunction(self, name, nLocals):
        '''
        Writes a VM function command.
        '''
        pass
    
    def writeReturn(self):
        '''
        Writes a VM return command.
        '''
        pass
    
    def close(self):
        '''
        Closes the output file
        '''
        pass
