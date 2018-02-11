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
        self.tokenizer = JackTokenizer(jackFile)#, DEBUG=DEBUG)
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
        Should only be called if keyword static or keyword field is the current
        token.
        """
        # Emit opening tag
        self.emit('<classVarDec>')

        # Eat either a 'static' or 'field' keyword
        self.eat('keyword', [ 'static', 'field' ])

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eat('keyword', [ 'int', 'char', 'boolean' ])
        else:
            self.eat('identifier')

        # Expect an identifier.
        self.eat('identifier')

        # Expect an optional list of identifiers.
        while t.tokenType() == 'symbol' and t.symbol() == ',':
            self.eat('symbol', ',')

            # Expect an identifier
            self.eat('identifier')

        # Expect symbol ';'
        self.eat('symbol', ';')

        # Emit closing tag
        self.emit('</classVarDec>')

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        Should only be called if the current token is one of 'constructor',
        'function', or 'method'.
        """
        # Emit opening tag
        self.emit('<subroutineDec>')

        # Eat keyword 'constructor', 'function', or 'method'.
        self.eat('keyword', [ 'constructor', 'function', 'method' ])

        # Expect 'void' or a type: one of the keywords 'int', 'char', or
        # 'boolean', or a className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eat('keyword', [ 'void', 'int', 'char', 'boolean' ])
        else:
            self.eat('identifier')

        # Expect an identifier.
        self.eat('identifier')

        # Expect symbol '('.
        self.eat('symbol', '(')

        # Expect a parameter list
        self.compileParameterList()

        # Expect symbol ')'.
        self.eat('symbol', ')')

        # Emit opening tag for subroutine body
        self.emit('<subroutineBody>')

        # Expect symbol '{'.
        self.eat('symbol', '{')

        # Expect varDec*
        while t.tokenType() == 'keyword' and t.keyWord() == 'var':
            self.compileVarDec()

        # Expect statements
        self.compileStatements()

        # Expect symbol '}'.
        self.eat('symbol', '}')

        # Emit closing tags
        self.emit('</subroutineBody>')
        self.emit('</subroutineDec>')

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing "( )".
        """
        # Emit opening tag
        self.emit('<parameterList>')

        # Alias for tokenizer
        t = self.tokenizer

        # Get the current token type
        tType = t.tokenType()

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        finished = False
        while not finished and tType in [ 'keyword', 'identifier' ]:
            if tType == 'keyword':
                self.eat('keyword', [ 'int', 'char', 'boolean' ])
            else:
                self.eat('identifier')

            # Expect varName (identifier)
            self.eat('identifier')

            # Look for a ',' symbol
            if t.tokenType() == 'symbol' and t.symbol() == ',':
                # If found, eat it
                self.eat('symbol', ',')

                # Get the next token type
                tType = t.tokenType()
            else:
                finished = True

        # Emit closing tag
        self.emit('</parameterList>')
        return

    def compileVarDec(self):
        """
        Compiles a var declaration.
        """
        # Emit opening tag
        self.emit('<varDec>')

        # Eat a 'var' keyword
        self.eat('keyword', 'var')

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eat('keyword', [ 'int', 'char', 'boolean' ])
        else:
            self.eat('identifier')

        # Expect an identifier.
        self.eat('identifier')

        # Expect an optional list of identifiers.
        while t.tokenType() == 'symbol' and t.symbol() == ',':
            self.eat('symbol', ',')

            # Expect an identifier
            self.eat('identifier')

        # Expect symbol ';'
        self.eat('symbol', ';')

        # Emit closing tag
        self.emit('</varDec>')

    def compileStatements(self):
        """
        Compiles a sequence of statements, not including the enclosing
        "{ }".
        """
        self.tokenizer.advance()

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
        if self.DEBUG: print('{}{}'.format(self.INDENT * self.indentLevel,
                                           xml))
        self.xmlFile.write('{}{}\n'.format(self.INDENT * self.indentLevel,
                                           xml))

        # If the XML does not contain '</', increase the indent level
        if '</' not in xml:
            self.indentLevel = self.indentLevel + 1
