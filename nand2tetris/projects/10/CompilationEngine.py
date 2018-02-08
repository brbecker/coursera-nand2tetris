from JackTokenizer import JackTokenizer

class CompilationEngine:
    """
    Effects the actual compilation output. Gets its input from a JackTokenizer
    and emits its parsed structure into an output file/stream.
    """

    INDENT = "  "

    def __init__(self, jackFile, xmlFile, DEBUG=False):
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass().
        """
        self.tokenizer = JackTokenizer(jackFile)
        self.xmlFile = open(xmlFile, mode='w')
        self.DEBUG = DEBUG

        # Indentation level
        self.indentLevel = 0

    def compileClass(self):
        """
        Compiles a complete class.
        """
        # Emit the class tag
        self.emit('<class>')

        # Alias self.tokenizer to make code more compact
        t = self.tokenizer

        # Verify that there is a token to read and advance to it
        if t.hasMoreTokens():
            # Advance to the next token
            t.advance()
        else:
            # If not, we're done.
            return

        # Expect KEYWORD 'class'
        self.eat('keyword', 'class')

        # Expect IDENTIFIER and advance if found
        self.eat('identifier')

        # Expect SYMBOL '{'
        self.eat('symbol', '{')

        # Expect zero or more classVarDecs
        while t.tokenType() == 'keyword' and \
            t.keyWord() in [ 'static', 'field' ]:
            self.compileClassVarDec()

        # Expect zero or more subroutineDecs
        while t.tokenType() == 'keyword' and \
            t.keyWord() in [ 'constructor', 'function', 'method' ]:
            self.compileSubroutine()

        # Expect SYMBOL '}'
        self.eat('symbol', '}')

        # Emit the end class tag
        self.emit('</class>')

    def compileClassVarDec(self):
        """
        Compiles a static declaration or a field declaration.
        """
        pass

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        """
        pass

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter lsit, not including the
        enclosing "( )".
        """
        pass

    def compileVarDec(self):
        """
        Compiles a var declaration.
        """
        pass

    def compileStatements(self):
        """
        Compiles a sequence of statements, not including the enclosing
        "{ }".
        """
        pass

    def compileDo(self):
        """
        Compiles a do statement.
        """
        pass

    def compileLet(self):
        """
        Compiles a let statement.
        """
        pass

    def compileWhile(self):
        """
        Compiles a while statement.
        """
        pass

    def compileReturn(self):
        """
        Compiles a return statement.
        """
        pass

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else
        clause.
        """
        pass

    def compileExpression(self):
        """
        Compiles an expression.
        """
        pass

    def compileTerm(self):
        """
        Compiles a term. This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must
        distinguish between a variable, an array entry, and a subroutine call.
        A single lookahead token, which may be one of "[", "(", or "."
        suffices to distinguish between the three possibilities. Any other
        token is not part of this term and should not be advanced over.
        """
        pass

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        """
        pass

    def eat(self, tokenType, tokenVals=[]):
        """
        Consume the current token if it matches the expected type and value.
        """
        # Get the type and value of the current token
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            tVal = t.keyWord()
        elif tType == 'symbol':
            tVal = t.symbol()
        elif tType == 'identifier':
            tVal = t.identifier()
        elif tType == 'integerConstant':
            tVal = t.intVal()
        else: # tType == 'stringConstant'
            tVal = t.stringVal()

        # If tokenVals is not a list, make it one
        if type(tokenVals) != type([]):
            tokenVals = [tokenVals]

        # Verify that the type matches and the value is one of the values
        # expected.
        if tType == tokenType and (not tokenVals or tVal in tokenVals):
            self.emit('<{0}>{1}</{0}>'.format(tType, tVal))
            t.advance()
        else:
            raise SyntaxError('Expected {} {}. Found {}.'.format(tokenType,
                                                                 ' or '.join(tokenVals),
                                                                 t.currentToken))

    def emit(self, xml):
        """
        Emit the provided XML data as a line to the xmlFile. Will indent based
        on the current indentLevel.
        """
        # If the XML starts with '</', reduce the indent level
        if xml[:2] == '</':
            self.indentLevel = self.indentLevel - 1

        # Output the XML, indented to the current level
        self.xmlFile.write('{}{}\n'.format(self.INDENT * self.indentLevel,
                                           xml))

        # If the XML does not contain '</', increase the indent level
        if '</' not in xml:
            self.indentLevel = self.indentLevel + 1
