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
            for line in f:
                # Strip comments and external whitespace
                line = Parser.COMMENT_PATTERN.sub('', line).strip()

                # Add to the queue if there is anything left on the line
                if line:
                    self._cmdqueue.append(line.lower())
                    if self._DEBUG:
                        print('Added: ' + line)

    def hasMoreCommands(self):
        if self._DEBUG:
            print('hmc (queue): ' + str(self._cmdqueue))
        return len(self._cmdqueue) != 0

    def advance(self):
        stmt = self._cmdqueue.popleft()
        if self._DEBUG:
            print('Popped: ' + stmt)

        # Match the command against the pattern
        match = Parser.COMMAND_PATTERN.match(stmt)

        # Get the command and convert it to the command type value
        cmd = match.group(1)
        if cmd in Parser.ARITH_CMDS:
            # All arithmetic commands map to C_ARITHMETIC and arg1 is set to the actual cmd
            Parser._ctype = Parser.C_ARITHMETIC
            Parser._arg1  = cmd
            Parser._arg2  = None
        else:
            # All other commands are indexed in CMDS
            Parser._ctype = Parser.CMDS.index(cmd)
            Parser._arg1  = match.group(3) or None
            Parser._arg2  = match.group(4) or None

        if self._DEBUG:
            print('ctype: {0}; arg1: {1}; arg2: {2}'.format(Parser._ctype, Parser._arg1, Parser._arg2))

    def commandType(self):
        pass

    def arg1(self):
        pass

    def arg2(self):
        pass

if __name__ == '__main__':
    # self-test code
    test = Parser(sys.argv[1], True)
    while test.hasMoreCommands():
        test.advance()
