class VMWriter():
    '''
    Emits VM commands into a file, using the VM command syntax.
    '''

    # Map Jack segment names to VM segment names.
    segments = {
        'ARG': 'argument',
        'CONST': 'constant',
        'LOCAL': 'local',
        'POINTER': 'pointer',
        'STATIC': 'static',
        'TEMP': 'temp',
        'THAT': 'that',
        'THIS': 'this',
    }

    def __init__(self, vmFile, DEBUG=False):
        '''
        Creates a new file and prepares it for writing.
        '''
        self.DEBUG = DEBUG
        self.vmFile = vmFile
        self.file = open(self.vmFile, mode='w')

        if self.DEBUG:
            print('DEBUG(VMWriter): Opened {} for writing'.format(self.vmFile))


    def writePush(self, segment, index):
        '''
        Writes a VM push command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): push {} {}'.format(segment, index))
        self.file.write('push {} {}\n'.format(self.segments[segment], index))


    def writePop(self, segment, index):
        '''
        Writes a VM pop command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): pop {} {}'.format(segment, index))
        self.file.write('pop {} {}\n'.format(self.segments[segment], index))


    def writeArithmetic(self, command):
        '''
        Writes a VM arithmetic command.
        '''
        # ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        if self.DEBUG:
            print('DEBUG(VMWriter): arithmetic {}'.format(command))


    def writeLabel(self, label):
        '''
        Writes a VM label command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): label {}'.format(label))


    def writeGoto(self, label):
        '''
        Writes a VM goto command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): goto {}'.format(label))


    def writeIf(self, label):
        '''
        Writes a VM if-goto command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): if {}'.format(label))


    def writeCall(self, name, nArgs):
        '''
        Writes a VM call command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): call {} {}'.format(name, nArgs))


    def writeFunction(self, name, nLocals):
        '''
        Writes a VM function command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): function {} {}'.format(name, nLocals))
        self.file.write('function {} {}\n'.format(name, nLocals))


    def writeReturn(self):
        '''
        Writes a VM return command.
        '''
        if self.DEBUG:
            print('DEBUG(VMWriter): return')


    def close(self):
        '''
        Closes the output file
        '''
        self.file.close()

        if self.DEBUG:
            print('DEBUG(VMWriter): Closed {}'.format(self.vmFile))
