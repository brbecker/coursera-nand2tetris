import re

class JackTokenizer:

    # Regular expressions (compiled for speed)
    PATTERN_BLANK_LINES = re.compile(r'(?m)^\s*$\n')
    PATTERN_MULTI_LINE_COMMENT = re.compile(r'(?s)\/\*.*?\*\/')
    PATTERN_SINGLE_LINE_COMMENT = re.compile(r'(?m)\s*//.*$')

    def __init__(self, jackFile, xmlFile, _DEBUG=False):
        self.xmlFile = xmlFile
        self._DEBUG = _DEBUG

        # Read the entire file into memory. Dangerous if the file is huge, but
        # unlikely.
        f = open(jackFile)
        c = f.read();
        f.close()

        # Remove multi-line comments. Comments in string literals will be a
        # problem.
        c = JackTokenizer.PATTERN_MULTI_LINE_COMMENT.sub('', c)

        # Remove single line comments. Comments in string literals will be a
        # problem.
        c = JackTokenizer.PATTERN_SINGLE_LINE_COMMENT.sub('', c)

        # Remove any blank lines.
        c = JackTokenizer.PATTERN_BLANK_LINES.sub('', c)

        # Save the comment-free Jack code
        self._jackData = c
        if _DEBUG: print(c)
