import os
from Parser import Parser

class CodeWriter:

    def __init__(self, filename, debug=False):
        self._outfile = open(filename, 'w')
        self._DEBUG = debug
        if self._DEBUG:
            self._asmInstCounter = 0

    def setFileName(self, filename):
        if not filename.endswith('.vm'):
            print("WARNING: filename does not have .vm extension: " + filename)
        self._vmfile = os.path.basename(filename)
        self._vmfilenoext = self._vmfile.replace('.vm', '')[:-3]

        # Initial "function" name is '_null'. Will be updated each time a
        # "function" is encountered.
        self._currFunction = '_null'

    def writeArithmetic(self, command, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

        # Set command to lower case
        command = command.lower()

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
                self.writeCode('@{0}-{1}-{2}'.format(self._vmfilenoext, lineno, command))
                self.writeCode('D;J{0}'.format(command.upper()))
                self.writeCode('@{0}-{1}-{2}'.format(self._vmfilenoext, lineno, 'out'))
                self.writeCode('D=0;JMP')
                self.writeCode('({0}-{1}-{2})'.format(self._vmfilenoext, lineno, command),
                               indent=False)
                self.writeCode('D=-1')
                self.writeCode('({0}-{1}-{2})'.format(self._vmfilenoext, lineno, 'out'),
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

    def writePushPop(self, ctype, segment, index, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

        # Set segment to lower case
        segment = segment.lower()

        # Error checking
        if ctype == Parser.C_POP and segment == 'constant':
            raise ValueError('pop not supported for constant segment: ' + cmdtext)
        if segment == 'pointer' and int(index) not in range(0, 2):
            raise ValueError('pointer segment only supports indexes 0 and 1: ' + cmdtext)
        if segment == 'temp' and int(index) not in range(0, 8):
            raise ValueError('temp segment only supports indexes from 0 to 7: ' + cmdtext)

        # Calculate the RAM address we really want

        # Load the index (offset/constant) into A
        self.writeCode('@{0}'.format(index))

        # Load the address in A
        if segment == 'constant':
            # No arithmetic required for constant
            pass
        elif segment in [ 'local', 'argument', 'this', 'that' ]:
            # Shift the offset into D
            self.writeCode('D=A')

            # Load the base address of the segment into A
            if segment == 'local':
                self.writeCode('@LCL')
            elif segment == 'argument':
                self.writeCode('@ARG')
            else:
                self.writeCode('@{0}'.format(segment.upper()))

            # Compute the desired final location
            self.writeCode('AD=D+M')
        elif segment in [ 'pointer', 'temp' ]:
            # Shift the offset into D
            self.writeCode('D=A')

            # Load the base address of the segment into A
            if segment == 'pointer':
                self.writeCode('@THIS')
            elif segment == 'temp':
                self.writeCode('@5')

            # Compute the desired final location (NOT indirect)
            self.writeCode('AD=D+A')
        elif segment == 'static':
            # For the static segment, just create a label and let the assembler deal with it
            self.writeCode('@{0}.{1}'.format(self._vmfile, index))
            if ctype == Parser.C_POP:
                # Copy the address to D if popping
                self.writeCode('D=A')
        else:
            raise ValueError('Unrecognized segment ' + segment)

        # push
        if ctype == Parser.C_PUSH:
            # Load the value into D (if not already there)
            if segment == 'constant':
                self.writeCode('D=A')
            else:
                self.writeCode('D=M')

            # Push D on to the stack
            self.writeCode('@SP')
            self.writeCode('A=M')
            self.writeCode('M=D')
            self.writeCode('@SP')
            self.writeCode('M=M+1')

        # Pop
        elif ctype == Parser.C_POP:
            # Save the calculated address in R13
            self.writeCode('@R13')
            self.writeCode('M=D')

            # Pop the value from the stack into D
            self.writeCode('@SP')
            self.writeCode('AM=M-1')
            self.writeCode('D=M')

            # Retrieve the address from R13 and save the value
            self.writeCode('@R13')
            self.writeCode('A=M')
            self.writeCode('M=D')

        else:
            raise ValueError('writePushPop: Unrecognized ctype {0}'.format(ctype))

        # Create a blank line in the ASM output after each VM command
        self.writeCode('', indent=False)

    def writeLabel(self, label, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

        # Output the ASM label
        self.writeCode('({0}${1})'.format(self._currFunction, label), indent=False)

        # Create a blank line in the ASM output after each VM command
        self.writeCode('', indent=False)

    def writeIf(self, label, cmdtext=None, lineno=None):
        if cmdtext and lineno:
            self.writeComment(self._vmfile, cmdtext, lineno)

        # Pop the top of the stack into D
        self.writeCode('@SP')
        self.writeCode('AM=M-1')
        self.writeCode('D=M')

        # Load the destination and jump if non-zero
        self.writeCode('@{0}${1}'.format(self._currFunction, label))
        self.writeCode('D;JNE')

        # Create a blank line in the ASM output after each VM command
        self.writeCode('', indent=False)

    def writeComment(self, vmfilename, cmdtext, lineno):
        self.writeCode('// {0} [{2}]: {1}'.format(vmfilename, cmdtext, lineno),
                       indent=False)

    # Simplify code generation by putting file specification in one place
    def writeCode(self, code, indent=True):
        if indent:
            code = ' ' * 4 + code
            if self._DEBUG:
                code = '{:<20}// {!s}'.format(code, self._asmInstCounter)
                self._asmInstCounter += 1

        print(code, file=self._outfile)

    def close(self):
        self._outfile.close()
