import os
from Parser import Parser

class CodeWriter:

    def __init__(self, filename, debug=False):
        self._outfile = open(filename, 'w')
        self._DEBUG = debug

    def setFileName(self, filename):
        self._vmfile = os.path.basename(filename)

    def writeArithmetic(self, command, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

        if command in [ 'neg', 'not' ]:
            # For the unary operations neg and not, we would pop the value,
            # perform the operation, and then push the result back on the
            # stack. For efficiency, just manipulate the value on the stack
            # directly. Saves the data copies and useless changes of SP.
            self.writeCode('@SP')
            self.writeCode('A=M-1')
            if command == 'neg':
                self.writeCode('M=-M')
            else:
                self.writeCode('M=!M')
        else:
            # For the binary operations, pop the second argument into D, then
            # perform the operation directly on the top of the stack.
            self.writeCode('@SP')
            self.writeCode('AM=M-1')
            self.writeCode('D=M')
            self.writeCode('A=A-1')

            if command == 'add':
                self.writeCode('M=D+M')
            elif command == 'sub':
                self.writeCode('M=M-D')
            elif command in [ 'eq', 'gt', 'lt' ]:
                self.writeCode('D=M-D')
                self.writeCode('@{0}-{1}-{2}'.format(self._vmfile, lineno, command))
                self.writeCode('D;J{0}'.format(command.upper()))
                self.writeCode('@{0}-{1}-{2}'.format(self._vmfile, lineno, 'out'))
                self.writeCode('D=0;JMP')
                self.writeCode('({0}-{1}-{2})'.format(self._vmfile, lineno, command),
                               indent=False)
                self.writeCode('D=-1')
                self.writeCode('({0}-{1}-{2})'.format(self._vmfile, lineno, 'out'),
                               indent=False)
                self.writeCode('@SP')
                self.writeCode('A=M-1')
                self.writeCode('M=D')
            elif command == 'and':
                self.writeCode('M=D&M')
            elif command == 'or':
                self.writeCode('M=M|D')
            else:
                print("WARNING: Unimplemented arithmetic command: " + command)

        # Create a blank line in the ASM output after each VM command
        self.writeCode('', indent=False)

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
            code = ' ' * 4 + code
        print(code, file=self._outfile)

    def close(self):
        self._outfile.close()
