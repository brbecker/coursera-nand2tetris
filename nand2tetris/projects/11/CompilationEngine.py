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
        self.emit(xml='<class>')

        # Alias self.tokenizer to make code more compact
        t = self.tokenizer

        # Verify that there is a token to read and advance to it
        if t.hasMoreTokens():
            # Advance to the next token
            t.advance()
        else:
            # If not, we're done.
            return

        self.eatAndEmit('keyword', ['class'])
        self.eat('identifier')
        self.eatAndEmit('symbol', ['{'])

        # Expect zero or more classVarDecs
        while t.tokenType() == 'keyword' and \
                t.keyWord() in ['static', 'field']:
            self.compileClassVarDec()

        # Expect zero or more subroutineDecs
        while t.tokenType() == 'keyword' and \
                t.keyWord() in ['constructor', 'function', 'method']:
            self.compileSubroutine()

        self.eatAndEmit('symbol', ['}'])
        self.emit(xml='</class>')

        # Should not be any more input
        if self.tokenizer.hasMoreTokens():
            raise SyntaxError('Token after end of class: ' + self.tokenizer.currentToken)

    def compileClassVarDec(self):
        """
        Compiles a static declaration or a field declaration.
        Should only be called if keyword static or keyword field is the current
        token.
        """
        self.emit(xml='<classVarDec>')
        self.eatAndEmit('keyword', ['static', 'field'])

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eatAndEmit('keyword', ['int', 'char', 'boolean'])
        else:
            self.eat('identifier')

        self.eat('identifier')

        # Expect an optional list of identifiers.
        while t.tokenType() == 'symbol' and t.symbol() == ',':
            self.eatAndEmit('symbol', [','])
            self.eat('identifier')

        self.eatAndEmit('symbol', [';'])
        self.emit(xml='</classVarDec>')

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        Should only be called if the current token is one of 'constructor',
        'function', or 'method'.
        """
        self.emit(xml='<subroutineDec>')
        self.eatAndEmit('keyword', ['constructor', 'function', 'method'])

        # Expect 'void' or a type: one of the keywords 'int', 'char', or
        # 'boolean', or a className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eatAndEmit('keyword', ['void', 'int', 'char', 'boolean'])
        else:
            self.eat('identifier')

        self.eat('identifier')
        self.eatAndEmit('symbol', ['('])
        self.compileParameterList()
        self.eatAndEmit('symbol', [')'])
        self.emit(xml='<subroutineBody>')
        self.eatAndEmit('symbol', ['{'])

        # Expect varDec*
        while t.tokenType() == 'keyword' and t.keyWord() == 'var':
            self.compileVarDec()

        self.compileStatements()
        self.eatAndEmit('symbol', ['}'])
        self.emit(xml='</subroutineBody>')
        self.emit(xml='</subroutineDec>')

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing "( )".
        """
        self.emit(xml='<parameterList>')

        # Alias for tokenizer
        t = self.tokenizer

        # Get the current token type
        tType = t.tokenType()

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        finished = False
        while not finished and tType in ['keyword', 'identifier']:
            if tType == 'keyword':
                self.eatAndEmit('keyword', ['int', 'char', 'boolean'])
            else:
                self.eat('identifier')

            self.eat('identifier')

            # Look for a ',' symbol
            if t.tokenType() == 'symbol' and t.symbol() == ',':
                # If found, eat it
                self.eatAndEmit('symbol', [','])

                # Get the next token type
                tType = t.tokenType()
            else:
                finished = True

        self.emit(xml='</parameterList>')

    def compileVarDec(self):
        """
        Compiles a var declaration.
        """
        self.emit(xml='<varDec>')
        self.eatAndEmit('keyword', ['var'])

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == 'keyword':
            self.eatAndEmit('keyword', ['int', 'char', 'boolean'])
        else:
            self.eat('identifier')

        self.eat('identifier')

        # Expect an optional list of identifiers.
        while t.tokenType() == 'symbol' and t.symbol() == ',':
            self.eatAndEmit('symbol', [','])
            self.eat('identifier')

        self.eatAndEmit('symbol', [';'])
        self.emit(xml='</varDec>')

    def compileStatements(self):
        """
        Compiles a sequence of statements, not including the enclosing
        "{ }".
        """
        self.emit(xml='<statements>')

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

        self.emit(xml='</statements>')

    def compileDo(self):
        """
        Compiles a do statement.
        """
        self.emit(xml='<doStatement>')
        self.eatAndEmit('keyword', ['do'])
        self.eat('identifier')

        # Check for a '.', which indicates a method call
        t = self.tokenizer
        if t.tokenType() == 'symbol' and t.symbol() == '.':
            self.eatAndEmit('symbol', ['.'])
            self.eat('identifier')

        self.eatAndEmit('symbol', ['('])
        self.compileExpressionList()
        self.eatAndEmit('symbol', [')'])
        self.eatAndEmit('symbol', [';'])
        self.emit(xml='</doStatement>')

    def compileLet(self):
        """
        Compiles a let statement.
        """
        self.emit(xml='<letStatement>')
        self.eatAndEmit('keyword', ['let'])
        self.eat('identifier')

        # Check for array qualifier
        t = self.tokenizer
        if t.tokenType() == 'symbol' and t.symbol() == '[':
            self.eatAndEmit('symbol', '[')
            self.compileExpression()
            self.eatAndEmit('symbol', [']'])

        self.eatAndEmit('symbol', ['='])
        self.compileExpression()
        self.eatAndEmit('symbol', [';'])
        self.emit(xml='</letStatement>')

    def compileWhile(self):
        """
        Compiles a while statement.
        """
        self.emit(xml='<whileStatement>')
        self.eatAndEmit('keyword', ['while'])
        self.eatAndEmit('symbol', ['('])
        self.compileExpression()
        self.eatAndEmit('symbol', [')'])
        self.eatAndEmit('symbol', ['{'])
        self.compileStatements()
        self.eatAndEmit('symbol', ['}'])
        self.emit(xml='</whileStatement>')

    def compileReturn(self):
        """
        Compiles a return statement.
        """
        self.emit(xml='<returnStatement>')
        self.eatAndEmit('keyword', ['return'])

        # If not a ';', expect an expression
        t = self.tokenizer
        if not (t.tokenType() == 'symbol' and t.symbol() == ';'):
            # Expect an expression
            self.compileExpression()

        self.eatAndEmit('symbol', [';'])
        self.emit(xml='</returnStatement>')

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else
        clause.
        """
        self.emit(xml='<ifStatement>')
        self.eatAndEmit('keyword', ['if'])
        self.eatAndEmit('symbol', ['('])
        self.compileExpression()
        self.eatAndEmit('symbol', [')'])
        self.eatAndEmit('symbol', ['{'])
        self.compileStatements()
        self.eatAndEmit('symbol', ['}'])

        t = self.tokenizer
        if t.tokenType() == 'keyword' and t.keyWord() == 'else':
            self.eatAndEmit('keyword', ['else'])
            self.eatAndEmit('symbol', ['{'])
            self.compileStatements()
            self.eatAndEmit('symbol', ['}'])

        self.emit(xml='</ifStatement>')

    def compileExpression(self):
        """
        Compiles an expression.
        """
        self.emit(xml='<expression>')
        self.compileTerm()

        # Look for operator-term pairs
        t = self.tokenizer
        ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        while t.tokenType() == 'symbol' and t.symbol() in ops:
            self.eatAndEmit('symbol', ops)
            self.compileTerm()

        self.emit(xml='</expression>')

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
        self.emit(xml='<term>')

        # Get the current token type
        t = self.tokenizer
        tType = t.tokenType()

        # Integer constant
        if tType == 'integerConstant':
            self.eatAndEmit('integerConstant')
        # String constant
        elif tType == 'stringConstant':
            self.eatAndEmit('stringConstant')
        # Keyword constant
        elif tType == 'keyword' and t.keyWord() in ['true', 'false', 'null', 'this']:
            self.eatAndEmit('keyword', ['true', 'false', 'null', 'this'])
        # Identifier (varName, or array name, or subroutine call)
        elif tType == 'identifier':
            self.eat('identifier')
            if t.tokenType() == 'symbol':
                symbol = t.symbol()
                if symbol == '[':
                    # Array reference
                    self.eatAndEmit('symbol', ['['])
                    self.compileExpression()
                    self.eatAndEmit('symbol', [']'])
                elif symbol == '(':
                    # Subroutine call
                    self.eatAndEmit('symbol', ['('])
                    self.compileExpressionList()
                    self.eatAndEmit('symbol', [')'])
                elif symbol == '.':
                    # Method call
                    self.eatAndEmit('symbol', ['.'])
                    self.eat('identifier')
                    self.eatAndEmit('symbol', ['('])
                    self.compileExpressionList()
                    self.eatAndEmit('symbol', [')'])
        # Sub-expression
        elif tType == 'symbol' and t.symbol() == '(':
            self.eatAndEmit('symbol', ['('])
            self.compileExpression()
            self.eatAndEmit('symbol', [')'])
        # Unary op and term
        elif tType == 'symbol' and t.symbol() in ['-', '~']:
            self.eatAndEmit('symbol', ['-', '~'])
            self.compileTerm()
        else:
            # Not a term
            raise SyntaxError('Expected term, found {}.'.format(t.currentToken))

        self.emit(xml='</term>')

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        """
        self.emit(xml='<expressionList>')

        # Get the initial token type
        t = self.tokenizer
        tType = t.tokenType()

        # Closing parenthesis ends the list
        while not (tType == 'symbol' and t.symbol() == ')'):
            self.compileExpression()

            # Expect an optional ','
            if t.tokenType() == 'symbol' and t.symbol() == ',':
                self.eatAndEmit('symbol', [','])

            # Update the tType
            tType = t.tokenType()

        self.emit(xml='</expressionList>')

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
        if not (tType == tokenType and (not tokenVals or tVal in tokenVals)):
            raise SyntaxError('Expected {} {}. Found {}.'.format(tokenType,
                                                                 ' or '.join(tokenVals or []),
                                                                 t.currentToken))

        if t.hasMoreTokens():
            t.advance()

        # Return the actual token type and value
        return (tType, tVal)

    def emit(self, token=None, xml=None):
        """
        Emit the provided XML or token as XML to the xmlFile.
        Will indent based on the current indentLevel.
        """
        # If XML code not provided, create it from the token type and value
        if not xml:
            (tokenType, tokenVal) = token
            xml = "<{0}>{1}</{0}>".format(tokenType, self.xmlProtect(tokenVal))

        # If the XML starts with '</', reduce the indent level
        if xml[:2] == '</':
            self.indentLevel = self.indentLevel - 1

        # Output the XML, indented to the current level
        output = '{}{}'.format(self.INDENT * self.indentLevel, xml)
        self.xmlFile.write(output)
        if self.DEBUG:
            print(output)

        # If the XML does not contain '</', increase the indent level
        if '</' not in xml:
            self.indentLevel = self.indentLevel + 1

    def xmlProtect(self, token):
        # Protect <, >, and & tokens from XML
        if token == '<':
            return '&lt;'
        elif token == '>':
            return '&gt;'
        elif token == '&':
            return '&amp;'
        else:
            return token

    def eatAndEmit(self, tokenType, tokenVals=None):
        # Shorthand for common pattern
        self.emit(token=self.eat(tokenType, tokenVals))
