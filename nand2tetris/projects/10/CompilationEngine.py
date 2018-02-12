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
        self.tokenizer = JackTokenizer(jackFile)  # , DEBUG=DEBUG)
        self.xmlFile = open(xmlFile, mode='w')
        self.DEBUG = DEBUG

        # Indentation level
        self.indentLevel = 0

    def compileClass(self):
        """
        Compiles a complete class.
        """
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

        self.eat('keyword', ['class'])
        self.eat('identifier')
        self.eat('symbol', ['{'])

        # Expect zero or more classVarDecs
        while t.tokenType() == 'keyword' and \
                t.keyWord() in ['static', 'field']:
            self.compileClassVarDec()

        # Expect zero or more subroutineDecs
        while t.tokenType() == 'keyword' and \
                t.keyWord() in ['constructor', 'function', 'method']:
            self.compileSubroutine()

        self.eat('symbol', ['}'])
        self.emit('</class>')

        # Should not be any more input
        if self.tokenizer.hasMoreTokens():
            raise SyntaxError('Token after end of class: ' + self.tokenizer.currentToken)

    def compileClassVarDec(self):
        """
        Compiles a static declaration or a field declaration.
        Should only be called if keyword static or keyword field is the current
        token.
        """
        self.emit('<classVarDec>')
        self.eat('keyword', ['static', 'field'])

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eat('keyword', ['int', 'char', 'boolean'])
        else:
            self.eat('identifier')

        self.eat('identifier')

        # Expect an optional list of identifiers.
        while t.tokenType() == 'symbol' and t.symbol() == ',':
            self.eat('symbol', [','])
            self.eat('identifier')

        self.eat('symbol', [';'])
        self.emit('</classVarDec>')

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        Should only be called if the current token is one of 'constructor',
        'function', or 'method'.
        """
        self.emit('<subroutineDec>')
        self.eat('keyword', ['constructor', 'function', 'method'])

        # Expect 'void' or a type: one of the keywords 'int', 'char', or
        # 'boolean', or a className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eat('keyword', ['void', 'int', 'char', 'boolean'])
        else:
            self.eat('identifier')

        self.eat('identifier')
        self.eat('symbol', ['('])
        self.compileParameterList()
        self.eat('symbol', [')'])
        self.emit('<subroutineBody>')
        self.eat('symbol', ['{'])

        # Expect varDec*
        while t.tokenType() == 'keyword' and t.keyWord() == 'var':
            self.compileVarDec()

        self.compileStatements()
        self.eat('symbol', ['}'])
        self.emit('</subroutineBody>')
        self.emit('</subroutineDec>')

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing "( )".
        """
        self.emit('<parameterList>')

        # Alias for tokenizer
        t = self.tokenizer

        # Get the current token type
        tType = t.tokenType()

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        finished = False
        while not finished and tType in ['keyword', 'identifier']:
            if tType == 'keyword':
                self.eat('keyword', ['int', 'char', 'boolean'])
            else:
                self.eat('identifier')

            self.eat('identifier')

            # Look for a ',' symbol
            if t.tokenType() == 'symbol' and t.symbol() == ',':
                # If found, eat it
                self.eat('symbol', [','])

                # Get the next token type
                tType = t.tokenType()
            else:
                finished = True

        self.emit('</parameterList>')

    def compileVarDec(self):
        """
        Compiles a var declaration.
        """
        self.emit('<varDec>')
        self.eat('keyword', ['var'])

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eat('keyword', ['int', 'char', 'boolean'])
        else:
            self.eat('identifier')

        self.eat('identifier')

        # Expect an optional list of identifiers.
        while t.tokenType() == 'symbol' and t.symbol() == ',':
            self.eat('symbol', [','])
            self.eat('identifier')

        self.eat('symbol', [';'])
        self.emit('</varDec>')

    def compileStatements(self):
        """
        Compiles a sequence of statements, not including the enclosing
        "{ }".
        """
        self.emit('<statements>')

        t = self.tokenizer
        while t.tokenType() == 'keyword':
            keyword = t.keyWord()
            if keyword == 'do':
                self.compileDo()
            elif keyword == 'let':
                self.compileLet()
            elif keyword == 'while':
                self.compileWhile()
            elif keyword == 'return':
                self.compileReturn()
            elif keyword == 'if':
                self.compileIf()
            else:
                raise SyntaxError('Expected statement. Found {}.'.format(t.currentToken))

        self.emit('</statements>')

    def compileDo(self):
        """
        Compiles a do statement.
        """
        self.emit('<doStatement>')
        self.eat('keyword', ['do'])
        self.eat('identifier')

        # Check for a '.', which indicates a method call
        t = self.tokenizer
        if t.tokenType() == 'symbol' and t.symbol() == '.':
            self.eat('symbol', ['.'])
            self.eat('identifier')

        self.eat('symbol', ['('])
        self.compileExpressionList()
        self.eat('symbol', [')'])
        self.eat('symbol', [';'])
        self.emit('</doStatement>')

    def compileLet(self):
        """
        Compiles a let statement.
        """
        self.emit('<letStatement>')
        self.eat('keyword', ['let'])
        self.eat('identifier')

        # Check for array qualifier
        t = self.tokenizer
        if t.tokenType() == 'symbol' and t.symbol() == '[':
            self.eat('symbol', '[')
            self.compileExpression()
            self.eat('symbol', [']'])

        self.eat('symbol', ['='])
        self.compileExpression()
        self.eat('symbol', [';'])
        self.emit('</letStatement>')

    def compileWhile(self):
        """
        Compiles a while statement.
        """
        self.emit('<whileStatement>')
        self.eat('keyword', ['while'])
        self.eat('symbol', ['('])
        self.compileExpression()
        self.eat('symbol', [')'])
        self.eat('symbol', ['{'])
        self.compileStatements()
        self.eat('symbol', ['}'])
        self.emit('</whileStatement>')

    def compileReturn(self):
        """
        Compiles a return statement.
        """
        self.emit('<returnStatement>')
        self.eat('keyword', ['return'])

        # If not a ';', expect an expression
        t = self.tokenizer
        if not (t.tokenType() == 'symbol' and t.symbol() == ';'):
            # Expect an expression
            self.compileExpression()

        self.eat('symbol', [';'])
        self.emit('</returnStatement>')

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else
        clause.
        """
        self.emit('<ifStatement>')
        self.eat('keyword', ['if'])
        self.eat('symbol', ['('])
        self.compileExpression()
        self.eat('symbol', [')'])
        self.eat('symbol', ['{'])
        self.compileStatements()
        self.eat('symbol', ['}'])

        t = self.tokenizer
        if t.tokenType() == 'keyword' and t.keyWord() == 'else':
            self.eat('keyword', ['else'])
            self.eat('symbol', ['{'])
            self.compileStatements()
            self.eat('symbol', ['}'])

        self.emit('</ifStatement>')

    def compileExpression(self):
        """
        Compiles an expression.
        """
        self.emit('<expression>')
        self.compileTerm()

        # Look for operator-term pairs
        t = self.tokenizer
        ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        while t.tokenType() == 'symbol' and t.symbol() in ops:
            self.eat('symbol', ops)
            self.compileTerm()

        self.emit('</expression>')

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
        self.emit('<term>')

        # Get the current token type
        t = self.tokenizer
        tType = t.tokenType()

        # Integer constant
        if tType == 'integerConstant':
            self.eat('integerConstant')
        # String constant
        elif tType == 'stringConstant':
            self.eat('stringConstant')
        # Keyword constant
        elif tType == 'keyword' and t.keyWord() in ['true', 'false', 'null', 'this']:
            self.eat('keyword', ['true', 'false', 'null', 'this'])
        # Identifier (varName, or array name, or subroutine call)
        elif tType == 'identifier':
            self.eat('identifier')
            if t.tokenType() == 'symbol':
                symbol = t.symbol()
                if symbol == '[':
                    # Array reference
                    self.eat('symbol', ['['])
                    self.compileExpression()
                    self.eat('symbol', [']'])
                elif symbol == '(':
                    # Subroutine call
                    self.eat('symbol', ['('])
                    self.compileExpressionList()
                    self.eat('symbol', [')'])
                elif symbol == '.':
                    # Method call
                    self.eat('symbol', ['.'])
                    self.eat('identifier')
                    self.eat('symbol', ['('])
                    self.compileExpressionList()
                    self.eat('symbol', [')'])
        # Sub-expression
        elif tType == 'symbol' and t.symbol() == '(':
            self.eat('symbol', ['('])
            self.compileExpression()
            self.eat('symbol', [')'])
        # Unary op and term
        elif tType == 'symbol' and t.symbol() in ['-', '~']:
            self.eat('symbol', ['-', '~'])
            self.compileTerm()
        else:
            # Not a term
            raise SyntaxError('Expected term, found {}.'.format(t.currentToken))

        self.emit('</term>')

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        """
        self.emit('<expressionList>')

        # Get the initial token type
        t = self.tokenizer
        tType = t.tokenType()

        # Closing parenthesis ends the list
        while not (tType == 'symbol' and t.symbol() == ')'):
            self.compileExpression()

            # Expect an optional ','
            if t.tokenType() == 'symbol' and t.symbol() == ',':
                self.eat('symbol', [','])

            # Update the tType
            tType = t.tokenType()

        self.emit('</expressionList>')

    def eat(self, tokenType, tokenVals=None):
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
        else:  # tType == 'stringConstant'
            tVal = t.stringVal()

        # Verify that the type matches and the value is one of the values
        # expected.
        if tType == tokenType and (not tokenVals or tVal in tokenVals):
            # Protect <, >, and & tokens from XML
            if tVal == '<':
                qtoken = '&lt;'
            elif tVal == '>':
                qtoken = '&gt;'
            elif tVal == '&':
                qtoken = '&amp;'
            else:
                qtoken = tVal

            self.emit('<{0}>{1}</{0}>'.format(tType, qtoken))
            if t.hasMoreTokens():
                t.advance()
        else:
            raise SyntaxError('Expected {} {}. Found {}.'.format(tokenType,
                                                                 ' or '.join(tokenVals or []),
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
        if self.DEBUG:
            print('{}{}'.format(self.INDENT * self.indentLevel, xml))
        self.xmlFile.write('{}{}\n'.format(self.INDENT * self.indentLevel, xml))

        # If the XML does not contain '</', increase the indent level
        if '</' not in xml:
            self.indentLevel = self.indentLevel + 1
