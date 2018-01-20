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

    def writeArithmetic(self, command):
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
            self.writePopD()
            self.writeCode('A=A-1')

            if command == 'add':
                self.writeCode('M=D+M')
            elif command == 'sub':
                self.writeCode('M=M-D')
            elif command in [ 'eq', 'gt', 'lt' ]:
                self.writeCode('D=M-D')
                self.writeCode('@{}-{}-{}'.format(self._vmfilenoext, lineno, command))
                self.writeCode('D;J{}'.format(command.upper()))
                self.writeCode('@{}-{}-{}'.format(self._vmfilenoext, lineno, 'out'))
                self.writeCode('D=0;JMP')
                self.writeCode('({}-{}-{})'.format(self._vmfilenoext, lineno, command),
                               indent=False)
                self.writeCode('D=-1')
                self.writeCode('({}-{}-{})'.format(self._vmfilenoext, lineno, 'out'),
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

    def writePushPop(self, ctype, segment, index):
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
        self.writeCode('@{}'.format(index))

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
                self.writeCode('@{}'.format(segment.upper()))

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
            self.writeCode('@{}.{}'.format(self._vmfile, index))
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
            self.writePushD()

        # Pop
        elif ctype == Parser.C_POP:
            # Save the calculated address in R13
            self.writeCode('@R13')
            self.writeCode('M=D')

            # Pop the value from the stack into D
            self.writePopD()

            # Retrieve the address from R13 and save the value
            self.writeCode('@R13')
            self.writeCode('A=M')
            self.writeCode('M=D')

        else:
            raise ValueError('writePushPop: Unrecognized ctype {}'.format(ctype))

    def writeLabel(self, label):
        # Output the ASM label
        self.writeCode('({}${})'.format(self._currFunction, label), indent=False)

    def writeGoto(self, label):
        # Load the destination and jump
        self.writeCode('@{}${}'.format(self._currFunction, label))
        self.writeCode('0;JMP')

    def writeIf(self, label):
        # Pop the top of the stack into D
        self.writePopD()

        # Load the destination and jump if non-zero
        self.writeCode('@{}${}'.format(self._currFunction, label))
        self.writeCode('D;JNE')

    def writeFunction(self, functionName, numLocals):
        # Output the label for the function and update current function
        self.writeCode('({})'.format(functionName), indent=False)
        self._currFunction = functionName

        # Set up for the local variables
        if int(numLocals) > 0:
            self.writeCode('@SP')
            self.writeCode('AD=M')
            for _ in range(int(numLocals)):
                self.writeCode('M=0')
                self.writeCode('AD=A+1')
            self.writeCode('@SP')
            self.writeCode('M=D')

    def writeReturn(self):
        # FRAME (R14) = LCL
        self.writeCode('@LCL')
        self.writeCode('D=M')
        self.writeCode('@R14')
        self.writeCode('M=D')

        # RET (R15) = *(FRAME-5)
        self.writeCode('@5')
        self.writeCode('A=D-A')
        self.writeCode('D=M')
        self.writeCode('@R15')
        self.writeCode('M=D')

        # *ARG = pop()
        self.writePopD()
        self.writeCode('@ARG')
        self.writeCode('A=M')
        self.writeCode('M=D')

        # SP = ARG+1
        self.writeCode('D=A+1')
        self.writeCode('@SP')
        self.writeCode('M=D')

        # THAT = *(FRAME-1)
        self.writeCode('@R14')
        self.writeCode('AM=M-1')
        self.writeCode('D=M')
        self.writeCode('@THAT')
        self.writeCode('M=D')

        # THIS = *(FRAME-2)
        self.writeCode('@R14')
        self.writeCode('AM=M-1')
        self.writeCode('D=M')
        self.writeCode('@THIS')
        self.writeCode('M=D')

        # ARG = *(FRAME-3)
        self.writeCode('@R14')
        self.writeCode('AM=M-1')
        self.writeCode('D=M')
        self.writeCode('@ARG')
        self.writeCode('M=D')

        # LCL = *(FRAME-4)
        self.writeCode('@R14')
        self.writeCode('AM=M-1')
        self.writeCode('D=M')
        self.writeCode('@LCL')
        self.writeCode('M=D')

        # goto RET
        self.writeCode('@R15')
        self.writeCode('A=M;JMP')

    def writePopD(self):
        # Pop into D
        self.writeCode('@SP')
        self.writeCode('AM=M-1')
        self.writeCode('D=M')

    def writePushD(self):
        # Push D on to the stack
        self.writeCode('@SP')
        self.writeCode('A=M')
        self.writeCode('M=D')
        self.writeCode('@SP')
        self.writeCode('M=M+1')

    def writeComment(self, cmdtext, lineno):
        self.writeCode('// {} [{}]: {}'.format(self._vmfile, lineno, cmdtext),
                       indent=False)

    def writeBlank(self):
        self.writeCode('', indent=False)

    # Simplify code generation by putting file specification in one place
    def writeCode(self, code, indent=True):
        if indent:
            code = ' ' * 4 + code
            if self._DEBUG:
                code = '{:<28}// {!s}'.format(code, self._asmInstCounter)
                self._asmInstCounter += 1

        print(code, file=self._outfile)

    def close(self):
        self._outfile.close()
