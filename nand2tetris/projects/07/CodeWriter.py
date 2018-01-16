class CodeWriter:

    def __init__(self, filename):
        self._outfile = open(filename, 'w')

    def setFileName(self, filename):
        self._vmfile = filename

    def writeArithmetic(self, command):
        pass

    def writePushPop(self, command, segment, index):
        pass

    def close(self):
        close(self._outfile)
