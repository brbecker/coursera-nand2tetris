import re

class JackTokenizer:

    # Token types
    (KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST) = range(5)

    # Regular expressions (compiled for speed)
    P_BLANK_LINES = re.compile(r'(?m)^\s*$\n')
    P_MULTI_LINE_COMMENT = re.compile(r'(?s)\/\*.*?\*\/')
    P_SINGLE_LINE_COMMENT = re.compile(r'(?m)\s*//.*$')

    R_KEYWORD = r'\b(?:class|constructor|function|method|field|static|var|' + \
                r'int|char|boolean|void|true|false|null|this|let|do|if|' + \
                r'else|while|return)\b'
    P_KEYWORD = re.compile(R_KEYWORD)

    R_SYMBOL = r'[\]\-{}()[.,;+*/&|<>=~]'
    P_SYMBOL = re.compile(R_SYMBOL)

    R_INTEGER_CONSTANT = r'[1-3]?\d{1,4}'
    P_INTEGER_CONSTANT = re.compile(R_INTEGER_CONSTANT)

    R_STRING_CONSTANT = r'"[^"]*"'
    P_STRING_CONSTANT = re.compile(R_STRING_CONSTANT)

    R_IDENTIFIER = r'[A-Za-z_][0-9A-Za-z_]*'
    P_IDENTIFIER = re.compile(R_IDENTIFIER)

    R_TOKEN = r'(?:' + R_KEYWORD + r')|(?:' + R_SYMBOL + r')|(?:' + \
                R_INTEGER_CONSTANT + r')|(?:' + R_STRING_CONSTANT + \
                r')|(?:' + R_IDENTIFIER + r')'
    P_TOKEN = re.compile(R_TOKEN)

    def __init__(self, jackFile, xmlFile, _DEBUG=False):
        self.xmlFile = xmlFile
        self._DEBUG = _DEBUG

        # Read the entire file into memory. Dangerous if the file is huge, but
        # unlikely.
        f = open(jackFile)
        s = f.read();
        f.close()

        # Remove multi-line comments. Comments in string literals will be a
        # problem.
        s = JackTokenizer.P_MULTI_LINE_COMMENT.sub('', s)

        # Remove single line comments. Comments in string literals will be a
        # problem.
        s = JackTokenizer.P_SINGLE_LINE_COMMENT.sub('', s)

        # Remove any blank lines.
        s = JackTokenizer.P_BLANK_LINES.sub('', s)

        # Save the comment-free Jack code after stripping any leading white
        # space.
        self._jackData = s.lstrip()
        if self._DEBUG: print(s)

        # Initialize the current token
        currentToken = None

    def hasMoreTokens(self):
        # Any non-whitespace character comprises a token.
        return self._jackData != ''

    def advance(self):
        # Look for a token at the beginning of the Jack data
        m = JackTokenizer.P_TOKEN.match(self._jackData)

        # We should always match something at the beginning of the Jack data
        # (or advance should not have been called)
        assert(m)
        assert(m.start() == 0)

        # Set the current token to the portion which matched
        self.currentToken = self._jackData[:m.end()]

        # Strip the token and any leading white space from the Jack data
        self._jackData = self._jackData[m.end():].lstrip()
        # if self._DEBUG: print('{:50}Next 10 chars: ^{}^'.format(self.currentToken, self._jackData[:10].replace('\n', '\\n')))

    def tokenType(self):
        if JackTokenizer.P_KEYWORD.fullmatch(self.currentToken):
            if self._DEBUG: print('{} is a KEYWORD'.format(self.currentToken))
            return JackTokenizer.KEYWORD
        elif JackTokenizer.P_SYMBOL.fullmatch(self.currentToken):
            if self._DEBUG: print('{} is a SYMBOL'.format(self.currentToken))
            return JackTokenizer.SYMBOL
        elif JackTokenizer.P_IDENTIFIER.fullmatch(self.currentToken):
            if self._DEBUG: print('{} is an IDENTIFIER'.format(self.currentToken))
            return JackTokenizer.IDENTIFIER
        elif JackTokenizer.P_INTEGER_CONSTANT.fullmatch(self.currentToken):
            if self._DEBUG: print('{} is an INT_CONST'.format(self.currentToken))
            return JackTokenizer.INT_CONST
        elif JackTokenizer.P_STRING_CONSTANT.fullmatch(self.currentToken):
            if self._DEBUG: print('{} is a STRING_CONST'.format(self.currentToken))
            return JackTokenizer.STRING_CONST

        # Should never get here
        assert(False)
