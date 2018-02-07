import re

class JackTokenizer:
    """
    Removes all comments and white space from the input stream and breaks it
    into Jack-language tokens, as specified in the Jack grammar.
    """

    # Token types
    (KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST) = range(5)

    # Keywords
    KEYWORDS = [ 'class', 'method', 'function', 'constructor', 'int',
                 'boolean', 'char', 'void', 'var',  'static', 'field', 'let',
                 'do', 'if', 'else', 'while', 'return', 'true', 'false',
                 'null', 'this' ]

    # Regular expressions (compiled for speed)
    P_BLANK_LINES = re.compile(r'(?m)^\s*$\n')
    P_MULTI_LINE_COMMENT = re.compile(r'(?s)\/\*.*?\*\/')
    P_SINGLE_LINE_COMMENT = re.compile(r'(?m)\s*//.*$')

    R_KEYWORD = r'\b(?:' + '|'.join(KEYWORDS) + r')\b'
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

    def __init__(self, jackFile, tokenizerFile=None, DEBUG=False):
        """
        Opens the input file/stream and gets ready to tokenize it.
        """
        self.DEBUG = DEBUG

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
        self.jackData = s.lstrip()
        if self.DEBUG: print(s)

        # Initialize the current token
        self.currentToken = None

        # Open and initializae the tokenizer file, if specified
        self.tokenizerFile = None
        if tokenizerFile:
            self.tokenizerFile = open(tokenizerFile, mode='w')
            self.tokenizerFile.write('<tokens>\n')

    def hasMoreTokens(self):
        """
        Do we have more tokens in the input?
        """
        # Any non-whitespace character comprises a token.
        if self.jackData != '':
            return True

        # If there are no more tokens and we are logging the tokenizer output,
        # finish it off.
        if self.tokenizerFile:
            self.tokenizerFile.write('</tokens>\n')
            self.tokenizerFile.close()
            self.tokenizerFile = None

        return False

    def advance(self):
        """
        Gets the next token from the input and makes it the current token.
        This method should only be called if hasMoreTokens() is True.
        Initially there is no current token.
        """
        # Look for a token at the beginning of the Jack data
        m = JackTokenizer.P_TOKEN.match(self.jackData)

        # We should always match something at the beginning of the Jack data
        # (or advance should not have been called)
        assert m, 'Did not match?'
        assert m.start() == 0, 'Did not match at the beginning?'

        # Set the current token to the portion which matched
        self.currentToken = self.jackData[:m.end()]

        # Strip the token and any leading white space from the Jack data
        self.jackData = self.jackData[m.end():].lstrip()
        # if self.DEBUG: print('{:50}Next 10 chars: ^{}^'.format(self.currentToken, self.jackData[:10].replace('\n', '\\n')))

    def tokenType(self):
        """
        Returns the type of the current token.
        """
        if JackTokenizer.P_KEYWORD.fullmatch(self.currentToken):
            if self.DEBUG: print('{} is a KEYWORD'.format(self.currentToken))
            return JackTokenizer.KEYWORD
        elif JackTokenizer.P_SYMBOL.fullmatch(self.currentToken):
            if self.DEBUG: print('{} is a SYMBOL'.format(self.currentToken))
            return JackTokenizer.SYMBOL
        elif JackTokenizer.P_IDENTIFIER.fullmatch(self.currentToken):
            if self.DEBUG: print('{} is an IDENTIFIER'.format(self.currentToken))
            return JackTokenizer.IDENTIFIER
        elif JackTokenizer.P_INTEGER_CONSTANT.fullmatch(self.currentToken):
            if self.DEBUG: print('{} is an INT_CONST'.format(self.currentToken))
            return JackTokenizer.INT_CONST
        elif JackTokenizer.P_STRING_CONSTANT.fullmatch(self.currentToken):
            if self.DEBUG: print('{} is a STRING_CONST'.format(self.currentToken))
            return JackTokenizer.STRING_CONST

        # Should never get here
        assert False, 'Unrecognized token' + self.currentToken

    def keyWord(self):
        """
        Returns the keyword which is the current token.
        Should be called only when tokenType() is KEYWORD.
        """
        assert self.tokenType() == JackTokenizer.KEYWORD, \
            'Current token is not a KEYWORD: ' + self.currentToken
        if self.tokenizerFile:
            self.tokenizerFile.write('  <keyword>' + \
                                     self.currentToken + \
                                     '</keyword>\n')
        return self.currentToken

    def symbol(self):
        """
        Returns the character which is the current token. Should be called
        only when tokenType() is KEYWORD.
        """
        token = self.currentToken
        assert self.tokenType() == JackTokenizer.SYMBOL, \
            'Current token is not a SYMBOL: ' + token

        # Protect <, >, and & tokens from XML
        if token == '<':
            token = '&lt;'
        elif token == '>':
            token = '&gt;'
        elif token == '&':
            token = '&amp;'

        if self.tokenizerFile:
            self.tokenizerFile.write('  <symbol>' + \
                                     token + \
                                     '</symbol>\n')
        return token

    def identifier(self):
        """
        Returns the identifier which is the current token.
        Should be called only when tokenType() is IDENTIFIER.
        """
        assert self.tokenType() == JackTokenizer.IDENTIFIER, \
            'Current token is not an IDENTIFIER: ' + self.currentToken
        if self.tokenizerFile:
            self.tokenizerFile.write('  <identifier>' + \
                                     self.currentToken + \
                                     '</identifier>\n')
        return self.currentToken

    def intVal(self):
        """
        Returns the integer value of the current token.
        Should be called only when tokenType() is INT_CONST.
        """
        assert self.tokenType() == JackTokenizer.INT_CONST, \
            'Current token is not an INT_CONST: ' + self.currentToken

        intVal = int(self.currentToken)
        assert intVal >= 0 and intVal <= 32767, \
            'INT_CONST value out of range [0, 32767]: ' + self.currentToken

        if self.tokenizerFile:
            self.tokenizerFile.write('  <integerConstant>' + \
                                     self.currentToken + \
                                     '</integerConstant>\n')
        return intVal

    def stringVal(self):
        """
        Returns the string value of the current token, without the double
        quotes. Should be called only when tokenType() is STRING_CONST.
        """
        assert self.tokenType() == JackTokenizer.STRING_CONST, \
            'Current token is not a STRING_CONST: ' + self.currentToken

        # Strip the double quotes
        strVal = self.currentToken[1:-1]

        if self.tokenizerFile:
            self.tokenizerFile.write('  <stringConstant>' + \
                                     strVal + \
                                     '</stringConstant>\n')
        return strVal
