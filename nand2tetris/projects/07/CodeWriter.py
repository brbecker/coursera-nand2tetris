class CodeWriter:

    def __init__(self, filename):
        self._outfile = open(filename, 'w')

    def setFileName(self, filename):
        self._vmfile = filename

    def writeArithmetic(self, command, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

    def writePushPop(self, command, segment, index, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

    def writeComment(self, vmfilename, cmdtext, lineno):
        print('// {0}[{2}]: {1}'.format(vmfilename, cmdtext, lineno),
              file=self._outfile)

    def close(self):
        close(self._outfile)
