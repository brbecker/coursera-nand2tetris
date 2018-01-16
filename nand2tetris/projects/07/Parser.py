import sys,re
from collections import deque

class Parser:

    # Command types
    ARITH_CMDS = [ 'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not' ]
    CMDS = [ 'ARITH', 'push', 'pop', 'label', 'goto', 'if-goto', 'function', 'call', 'return' ]
    (C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL) = range(len(CMDS))

    # Regular expressions (compiled for speed)
    COMMENT_PATTERN = re.compile(r'//.*$')
    COMMAND_PATTERN = re.compile(r'^(\S+)\s*((\S+)\s*(\S+)?)?$')

    def __init__(self, filename, debug=False):
        self._DEBUG = debug
        self._cmdqueue = deque()
        with open(filename) as f:
            lineno = 0
            for line in f:
                lineno += 1

                # Strip comments and external whitespace, to leave only the command
                cmd = Parser.COMMENT_PATTERN.sub('', line).strip()

                # Add to the queue if there is anything left as a command
                if cmd:
                    tup = (cmd.lower(), line, lineno)
                    self._cmdqueue.append(tup)
                    if self._DEBUG:
                        print('Queued: ' + str(tup))
        self._command = self._line = self._lineno = None

    def hasMoreCommands(self):
        if self._DEBUG:
            print('hmc (queue): ' + str(self._cmdqueue))
        return len(self._cmdqueue) != 0

    def advance(self):
        (self._command, self._line, self._lineno) = self._cmdqueue.popleft()
        if self._DEBUG:
            print('Popped "{0}" from line {2}: {1}'.format(self._command, self._line.strip(), self._lineno))

        # Match the command against the pattern
        match = Parser.COMMAND_PATTERN.match(self._command)

        # Get the command and convert it to the command type value
        cmd = match.group(1)
        if cmd in Parser.ARITH_CMDS:
            # All arithmetic commands map to C_ARITHMETIC and arg1 is set to the actual cmd
            self._ctype = Parser.C_ARITHMETIC
            self._arg1  = cmd
            self._arg2  = None
        else:
            # All other commands are indexed in CMDS
            self._ctype = Parser.CMDS.index(cmd)
            self._arg1  = match.group(3) or None
            self._arg2  = match.group(4) or None

        if self._DEBUG:
            print('ctype: {0}; arg1: {1}; arg2: {2}'.format(self._ctype, self._arg1, self._arg2))

    def commandType(self):
        return self._ctype

    def arg1(self):
        if self.commandType() == Parser.C_RETURN:
            raise ValueError("arg1: Illegal command: return")
        return self._arg1

    def arg2(self):
        if self.commandType() not in [Parser.C_PUSH, Parser.C_POP, Parser.C_FUNCTION, Parser.C_CALL]:
            raise ValueError("arg2: Illegal command: must be push, pop, function, or call")
        return self._arg2

    def command(self):
        return self._command

    def origline(self):
        return self._line

    def lineno(self):
        return self._lineno

if __name__ == '__main__':
    # self-test code
    test = Parser(sys.argv[1], True)
    while test.hasMoreCommands():
        test.advance()
