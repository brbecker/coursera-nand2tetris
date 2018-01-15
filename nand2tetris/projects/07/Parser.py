import re
from collections import deque

class Parser:

    # Command types
    (C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL) = range(9)

    # Regular expressions (compiled for speed)
    COMMENT_PATTERN   = re.compile(r'//.*$')

    def __init__(self, filename):
        self._cmdqueue = deque()
        with open(filename) as f:
            for line in f:
                # Strip comments and external whitespace
                line = Parser.COMMENT_PATTERN.sub('', line).strip()

                # Add to the queue if there is anything left on the line
                if line:
                    self._cmdqueue.append(line)
                    # print('Added: ' + line)

    def hasMoreCommands(self):
        pass

    def advance(self):
        pass

    def commandType(self):
        pass

    def arg1(self):
        pass

    def arg2(self):
        pass
