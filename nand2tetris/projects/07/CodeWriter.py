from Parser import Parser

class CodeWriter:

    def __init__(self, filename, debug=False):
        self._outfile = open(filename, 'w')
        self._DEBUG = debug

    def setFileName(self, filename):
        self._vmfile = filename

    def writeArithmetic(self, command, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

    def writePushPop(self, command, segment, index, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

        # push constant 7
        if segment == 'constant':
            if command == Parser.C_PUSH:
                self.writeCode('@{0}'.format(index))
                self.writeCode('D=A')
                self.writeCode('@SP')
                self.writeCode('A=M')
                self.writeCode('M=D')
                self.writeCode('@SP')
                self.writeCode('M=M+1')
            else:
                print("ERROR: pop not supported for constant segment: " + cmdtext)
        else:
            print("WARNING: Unimplemented segment: " + segment)

        # Create a blank line in the ASM output after each VM command
        self.writeCode('', indent=False)

    def writeComment(self, vmfilename, cmdtext, lineno):
        self.writeCode('// {0} [{2}]: {1}'.format(vmfilename, cmdtext, lineno),
                       indent=False)

    # Simplify code generation by putting file specification in one place
    def writeCode(self, code, indent=True):
        if indent:
            code = '    ' + code
        print(code, file=self._outfile)

    def close(self):
        self._outfile.close()
