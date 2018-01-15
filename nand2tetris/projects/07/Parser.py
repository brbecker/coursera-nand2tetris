class Parser:

    # Command types
    (C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL) = range(9)

    def __init__(self, filename):
        pass

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
