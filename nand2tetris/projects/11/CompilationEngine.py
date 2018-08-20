from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """
    Effects the actual compilation output. Gets its input from a JackTokenizer
    and emits its parsed structure into an output file/stream.
    """

    INDENT = "  "

    def __init__(self, jackFile, vmFile, DEBUG=False):
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass().
        """
        self.tokenizer = JackTokenizer(jackFile)  # , DEBUG=DEBUG)
        self.DEBUG = DEBUG

        # Indentation level
        self.indentLevel = 0

        # Counters for while loops and if statements
        self.whileCounter = self.ifCounter = 0

        # Initialize the symbol table
        self.symtab = SymbolTable(DEBUG=True)

        # Initialize the VM writer
        self.writer = VMWriter(vmFile, DEBUG=True)

    def compileClass(self):
        """
        Compiles a complete class.
        """
        self.emit(xml="<class>")

        # Alias self.tokenizer to make code more compact
        t = self.tokenizer

        # Verify that there is a token to read and advance to it
        if t.hasMoreTokens():
            # Advance to the next token
            t.advance()
        else:
            # If not, we're done.
            return

        self.eatAndEmit("keyword", ["class"])
        (_, self.thisClass) = self.eatAndEmit(
            "identifier", category="CLASS", state="DEFINE"
        )
        self.eatAndEmit("symbol", ["{"])

        # Expect zero or more classVarDecs. Count the fields defined.
        self.nFields = 0
        while t.tokenType() == "keyword" and t.keyWord() in ["static", "field"]:
            kw = t.keyWord()
            count = self.compileClassVarDec()

            # Count the fields to determine the size of the object
            if kw == "field":
                self.nFields += count

        # Expect zero or more subroutineDecs
        while t.tokenType() == "keyword" and t.keyWord() in [
            "constructor",
            "function",
            "method",
        ]:
            self.compileSubroutine()

        self.eatAndEmit("symbol", ["}"])
        self.emit(xml="</class>")

        # Should not be any more input
        if self.tokenizer.hasMoreTokens():
            raise SyntaxError(
                "Token after end of class: " + self.tokenizer.currentToken
            )

        # Close the VMWriter
        self.writer.close()

    def compileClassVarDec(self):
        """
        Compiles a static declaration or a field declaration.
        Should only be called if keyword static or keyword field is the current
        token.
        """
        self.emit(xml="<classVarDec>")

        # Need to save the variable kind for the symbol table
        token = self.eat("keyword", ["static", "field"])
        (_, varKind) = token
        varKind = varKind.upper()
        self.emit(token=token)

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == "keyword":
            self.eatAndEmit("keyword", ["int", "char", "boolean"])
        else:
            self.eatAndEmit("identifier", category="CLASS", state="USE")

        self.eatAndEmit("identifier", category=varKind, state="DEFINE")
        count = 1

        # Expect an optional list of identifiers.
        while t.tokenType() == "symbol" and t.symbol() == ",":
            self.eatAndEmit("symbol", [","])
            self.eatAndEmit("identifier", category=varKind, state="DEFINE")
            count += 1

        self.eatAndEmit("symbol", [";"])
        self.emit(xml="</classVarDec>")

        return count

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        Should only be called if the current token is one of 'constructor',
        'function', or 'method'.
        """
        self.emit(xml="<subroutineDec>")
        (_, kw) = self.eatAndEmit("keyword", ["constructor", "function", "method"])

        # Reset the subroutine symbol table
        self.symtab.startSubroutine()

        # If this is a method, seed the symbol table with "this" as argument 0
        if kw == "method":
            self.symtab.define("this", self.thisClass, "ARG")

        # Expect 'void' or a type: one of the keywords 'int', 'char', or
        # 'boolean', or a className (identifier).
        t = self.tokenizer
        tType = t.tokenType()
        if tType == "keyword":
            self.eatAndEmit("keyword", ["void", "int", "char", "boolean"])
        else:
            self.eatAndEmit("identifier", category="CLASS", state="USE")

        (_, functionName) = self.eatAndEmit(
            "identifier", category="SUBROUTINE", state="DEFINE"
        )

        self.eatAndEmit("symbol", ["("])
        self.compileParameterList()
        self.eatAndEmit("symbol", [")"])
        self.emit(xml="<subroutineBody>")
        self.eatAndEmit("symbol", ["{"])

        # Expect varDec*. Count the number of local variables.
        nLocals = 0
        while t.tokenType() == "keyword" and t.keyWord() == "var":
            nLocals += self.compileVarDec()

        # Generate the VM code to start the function.
        self.writer.writeFunction("{}.{}".format(self.thisClass, functionName), nLocals)

        # If this subroutine is a constructor, allocate memory for the new object and set the base of the this segment
        if kw == "constructor":
            self.writer.writePush("CONST", self.nFields)
            self.writer.writeCall("Memory.alloc", 1)
            self.writer.writePop("POINTER", 0)

        # If this subroutine is a method, set the base of the this segment
        if kw == "method":
            self.writer.writePush("ARG", 0)
            self.writer.writePop("POINTER", 0)

        # Compile the code of the function
        self.compileStatements()
        self.eatAndEmit("symbol", ["}"])
        self.emit(xml="</subroutineBody>")
        self.emit(xml="</subroutineDec>")

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing '( )'.
        """
        self.emit(xml="<parameterList>")

        # Alias for tokenizer
        t = self.tokenizer

        # Get the current token type
        tType = t.tokenType()

        # Expect a type: one of the keywords 'int', 'char', or 'boolean', or a
        # className (identifier).
        finished = False
        while not finished and tType in ["keyword", "identifier"]:
            if tType == "keyword":
                (_, varType) = self.eatAndEmit("keyword", ["int", "char", "boolean"])
            else:
                (_, varType) = self.eatAndEmit(
                    "identifier", category="CLASS", state="USE"
                )

            self.eatAndEmit(
                "identifier", category="ARG", state="DEFINE", varType=varType
            )

            # Look for a ',' symbol
            if t.tokenType() == "symbol" and t.symbol() == ",":
                # If found, eat it
                self.eatAndEmit("symbol", [","])

                # Get the next token type
                tType = t.tokenType()
            else:
                finished = True

        self.emit(xml="</parameterList>")

    def compileVarDec(self):
        """
        Compiles a var declaration.
        """
        self.emit(xml="<varDec>")
        self.eatAndEmit("keyword", ["var"])

        # Expect a type for the variable: one of the keywords 'int', 'char',
        # or 'boolean', or a className (identifier). Save the variable type.
        t = self.tokenizer
        tType = t.tokenType()
        if tType == "keyword":
            (_, varType) = self.eatAndEmit("keyword", ["int", "char", "boolean"])
        else:
            (_, varType) = self.eatAndEmit("identifier", category="CLASS", state="USE")

        self.eatAndEmit("identifier", category="VAR", state="DEFINE", varType=varType)
        nVars = 1

        # Expect an optional list of identifiers.
        while t.tokenType() == "symbol" and t.symbol() == ",":
            self.eatAndEmit("symbol", [","])
            self.eatAndEmit(
                "identifier", category="VAR", state="DEFINE", varType=varType
            )
            nVars += 1

        self.eatAndEmit("symbol", [";"])
        self.emit(xml="</varDec>")

        return nVars

    def compileStatements(self):
        """
        Compiles a sequence of statements, not including the enclosing
        '{ }'.
        """
        self.emit(xml="<statements>")

        t = self.tokenizer
        while t.tokenType() == "keyword":
            keyword = t.keyWord()
            if keyword == "do":
                self.compileDo()
            elif keyword == "let":
                self.compileLet()
            elif keyword == "while":
                self.compileWhile()
            elif keyword == "return":
                self.compileReturn()
            elif keyword == "if":
                self.compileIf()
            else:
                raise SyntaxError(
                    "Expected statement. Found {}.".format(t.currentToken)
                )

        self.emit(xml="</statements>")

    def compileDo(self):
        """
        Compiles a do statement.
        """
        self.emit(xml="<doStatement>")
        self.eatAndEmit("keyword", ["do"])

        # Eat the identifier. Can't emit until we know if this is a class or a subroutine.
        token = self.eat("identifier")
        (_, ident) = token

        # Check for a '.', which indicates a method call
        t = self.tokenizer
        if t.tokenType() == "symbol" and t.symbol() == ".":
            self.eatAndEmit("symbol", ["."])
            # Previous token was an object or a class. Check symbol table.
            objType = self.symtab.typeOf(ident)
            if objType:
                # ident is an object, so method is objType.method, and the object must be loaded into this as argument 0
                self.emit(token=token, category=self.symtab.kindOf(ident), state="USE")

                # subroutine starts with the class type
                subroutine = objType

                # Add an argument to the stack for "this"
                nArgs = 1
                kind = self.symtab.kindOf(ident)
                index = self.symtab.indexOf(ident)
                self.writer.writePush(kind, index)
            else:
                # ident is a class, so method is ident.method and there is no this
                self.emit(token=token, category="CLASS", state="USE")
                subroutine = ident
                nArgs = 0

            methodToken = self.eat("identifier")
            (_, method) = methodToken
            self.emit(token=methodToken, category="METHOD", state="USE")
            subroutine += "." + method
        else:
            # Bare subroutine calls are assumed to be methods of the current class
            self.emit(token=token, category="SUBROUTINE", state="USE")
            subroutine = self.thisClass + "." + ident

            # Add "this" to the stack
            nArgs = 1
            self.writer.writePush("POINTER", 0)

        self.eatAndEmit("symbol", ["("])
        nArgs += self.compileExpressionList()
        self.eatAndEmit("symbol", [")"])
        self.eatAndEmit("symbol", [";"])

        # Call the desired subroutine and consume the returned value
        self.writer.writeCall(subroutine, nArgs)
        self.writer.writePop("TEMP", 0)

        self.emit(xml="</doStatement>")

    def compileLet(self):
        """
        Compiles a let statement.
        """
        self.emit(xml="<letStatement>")
        self.eatAndEmit("keyword", ["let"])
        (_, varName) = self.eatAndEmit("identifier", category="LET", state="USE")

        # Look up the variable in the symbol table
        varKind = self.symtab.kindOf(varName)
        varIndex = self.symtab.indexOf(varName)

        # Check for array qualifier
        t = self.tokenizer
        if t.tokenType() == "symbol" and t.symbol() == "[":
            # TODO
            self.eatAndEmit("symbol", "[")
            self.compileExpression()
            self.eatAndEmit("symbol", ["]"])

        self.eatAndEmit("symbol", ["="])
        self.compileExpression()
        self.eatAndEmit("symbol", [";"])

        # Value to save is at the top of the stack.
        self.writer.writePop(varKind, varIndex)

        self.emit(xml="</letStatement>")

    def compileWhile(self):
        """
        Compiles a while statement.
        """
        self.emit(xml="<whileStatement>")
        self.eatAndEmit("keyword", ["while"])
        
        whileInstance = self.whileCounter
        self.whileCounter += 1
        self.writer.writeLabel("WHILE.{}.{}.EXP".format(self.thisClass, whileInstance))

        self.eatAndEmit("symbol", ["("])
        self.compileExpression()
        self.eatAndEmit("symbol", [")"])

        self.writer.writeArithmetic("U~")
        self.writer.writeIf("WHILE.{}.{}.EXIT".format(self.thisClass, whileInstance))

        self.eatAndEmit("symbol", ["{"])
        self.compileStatements()
        self.eatAndEmit("symbol", ["}"])

        self.writer.writeGoto("WHILE.{}.{}.EXP".format(self.thisClass, whileInstance))
        self.writer.writeLabel("WHILE.{}.{}.EXIT".format(self.thisClass, whileInstance))

        self.emit(xml="</whileStatement>")

    def compileReturn(self):
        """
        Compiles a return statement.
        """
        self.emit(xml="<returnStatement>")
        self.eatAndEmit("keyword", ["return"])

        # If not a ';', expect an expression
        t = self.tokenizer
        if not (t.tokenType() == "symbol" and t.symbol() == ";"):
            # Expect an expression
            self.compileExpression()
        else:
            # void function, so force a 0 onto the stack to return
            self.writer.writePush("CONST", 0)

        self.writer.writeReturn()
        self.eatAndEmit("symbol", [";"])
        self.emit(xml="</returnStatement>")

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else
        clause.
        """
        self.emit(xml="<ifStatement>")
        self.eatAndEmit("keyword", ["if"])
        self.eatAndEmit("symbol", ["("])
        self.compileExpression()
        self.eatAndEmit("symbol", [")"])

        self.writer.writeArithmetic("U~")
        ifInstance = self.ifCounter
        self.ifCounter += 1
        self.writer.writeIf("IF.{}.{}.ELSE".format(self.thisClass, ifInstance))

        self.eatAndEmit("symbol", ["{"])
        self.compileStatements()
        self.eatAndEmit("symbol", ["}"])

        self.writer.writeGoto("IF.{}.{}.EXIT".format(self.thisClass, ifInstance))
        self.writer.writeLabel("IF.{}.{}.ELSE".format(self.thisClass, ifInstance))

        t = self.tokenizer
        if t.tokenType() == "keyword" and t.keyWord() == "else":
            self.eatAndEmit("keyword", ["else"])
            self.eatAndEmit("symbol", ["{"])
            self.compileStatements()
            self.eatAndEmit("symbol", ["}"])

        self.writer.writeLabel("IF.{}.{}.EXIT".format(self.thisClass, ifInstance))

        self.emit(xml="</ifStatement>")

    def compileExpression(self):
        """
        Compiles an expression.
        """
        self.emit(xml="<expression>")
        self.compileTerm()

        # Look for operator-term pairs
        t = self.tokenizer
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        while t.tokenType() == "symbol" and t.symbol() in ops:
            (_, op) = self.eatAndEmit("symbol", ops)
            self.compileTerm()
            self.writer.writeArithmetic(op)

        self.emit(xml="</expression>")

    def compileTerm(self):
        """
        Compiles a term. This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must
        distinguish between a variable, an array entry, and a subroutine call.
        A single lookahead token, which may be one of '[', '(', or '.',
        suffices to distinguish between the three possibilities. Any other
        token is not part of this term and should not be advanced over.
        """
        self.emit(xml="<term>")

        # Get the current token type
        t = self.tokenizer
        tType = t.tokenType()

        # Integer constant
        if tType == "integerConstant":
            (_, value) = self.eatAndEmit("integerConstant")
            self.writer.writePush("CONST", value)
        # String constant
        elif tType == "stringConstant":
            self.eatAndEmit("stringConstant")
        # Keyword constant
        elif tType == "keyword" and t.keyWord() in ["true", "false", "null", "this"]:
            (_, kw) = self.eatAndEmit("keyword", ["true", "false", "null", "this"])
            if kw in ["null", "false"]:
                # Map to 0
                self.writer.writePush("CONST", 0)
            elif kw == "true":
                # Map to -1
                self.writer.writePush("CONST", 1)
                self.writer.writeArithmetic("U-")  # NEG
            else:
                # this
                self.writer.writePush("POINTER", 0)
        # Identifier (varName, or array name, or subroutine call)
        elif tType == "identifier":
            (_, ident) = self.eatAndEmit("identifier", category="TERM", state="USE")
            if t.tokenType() == "symbol":
                symbol = t.symbol()
                if symbol == "[":
                    # Array reference
                    # ident is the array name
                    self.eatAndEmit("symbol", ["["])
                    self.compileExpression()
                    self.eatAndEmit("symbol", ["]"])
                elif symbol == "(":
                    # Subroutine call
                    # ident is the subroutine.
                    self.eatAndEmit("symbol", ["("])
                    nArgs = self.compileExpressionList()
                    self.eatAndEmit("symbol", [")"])
                    self.writer.writeCall(ident, nArgs)
                elif symbol == ".":
                    # Method call.
                    # ident is the class name (static method) or the object which will be argument 0 (this).

                    # Look up the object's type in the symbol table. If not found, then it is a class name and there is no object to be "this".
                    objType = self.symtab.typeOf(ident)
                    if objType is not None:
                        # Push this onto stack as argument 0
                        # TODO: How?
                        addSelf = 1
                        raise NotImplementedError("Need to push this onto stack")
                    else:
                        # ident is the class name, so use it
                        objType = ident
                        addSelf = 0

                    self.eatAndEmit("symbol", ["."])
                    (_, method) = self.eatAndEmit(
                        "identifier", category="SUBROUTINE", state="USE"
                    )
                    self.eatAndEmit("symbol", ["("])
                    nArgs = self.compileExpressionList()
                    self.eatAndEmit("symbol", [")"])
                    self.writer.writeCall(objType + "." + method, nArgs + addSelf)
                else:
                    # Next token not a symbol, so ident is a simple variable identifier.
                    varKind = self.symtab.kindOf(ident)
                    varIndex = self.symtab.indexOf(ident)
                    self.writer.writePush(varKind, varIndex)
        # Sub-expression
        elif tType == "symbol" and t.symbol() == "(":
            self.eatAndEmit("symbol", ["("])
            self.compileExpression()
            self.eatAndEmit("symbol", [")"])
        # Unary op and term
        elif tType == "symbol" and t.symbol() in ["-", "~"]:
            (_, op) = self.eatAndEmit("symbol", ["-", "~"])
            self.compileTerm()
            # Mark as unary to get right version of '-'
            self.writer.writeArithmetic("U" + op)
        else:
            # Not a term
            raise SyntaxError("Expected term, found {}.".format(t.currentToken))

        self.emit(xml="</term>")

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        Returns the number of expressions compiled.
        """
        self.emit(xml="<expressionList>")

        # Get the initial token type
        t = self.tokenizer
        tType = t.tokenType()

        # Count the expressions in the list
        nExpressions = 0

        # Closing parenthesis ends the list
        while not (tType == "symbol" and t.symbol() == ")"):
            nExpressions += 1
            self.compileExpression()

            # Expect an optional ','
            if t.tokenType() == "symbol" and t.symbol() == ",":
                self.eatAndEmit("symbol", [","])

            # Update the tType
            tType = t.tokenType()

        self.emit(xml="</expressionList>")

        return nExpressions

    def eat(self, tokenType, tokenVals=None):
        """
        Consume the current token if it matches the expected type and value.
        """
        # Get the type and value of the current token
        t = self.tokenizer
        tType = t.tokenType()
        if tType == "keyword":
            tVal = t.keyWord()
        elif tType == "symbol":
            tVal = t.symbol()
        elif tType == "identifier":
            tVal = t.identifier()
        elif tType == "integerConstant":
            tVal = t.intVal()
        else:  # tType == 'stringConstant'
            tVal = t.stringVal()

        # Verify that the type matches and the value is one of the values
        # expected.
        if not (tType == tokenType and (not tokenVals or tVal in tokenVals)):
            raise SyntaxError(
                "Expected {} {}. Found {}.".format(
                    tokenType, " or ".join(tokenVals or []), t.currentToken
                )
            )

        if t.hasMoreTokens():
            t.advance()

        # Return the actual token type and value
        return (tType, tVal)

    def emit(self, token=None, category=None, state=None, varType=None, xml=None):
        """
        Emit the provided XML or token as XML to the xmlFile.
        Will indent based on the current indentLevel.
        """
        # If XML code not provided, create it from the token type and value
        if not xml:
            (tokenType, tokenVal) = token

            # Handle symbol table additions/lookups
            index = None
            if state == "DEFINE" and category in ["STATIC", "FIELD", "ARG", "VAR"]:
                index = self.symtab.define(tokenVal, varType, category)

            if state == "USE" and category in ["LET", "TERM"]:
                category = self.symtab.kindOf(tokenVal)
                if category:
                    varType = self.symtab.typeOf(tokenVal)
                    index = self.symtab.indexOf(tokenVal)
                else:
                    category = "CLASS OR SUBROUTINE"

            # Define additional output fields
            fields = ""
            if category is not None:
                fields += " category={}".format(category)
            if state is not None:
                fields += " state={}".format(state)
            if varType is not None:
                fields += " varType={}".format(varType)
            if index is not None:
                fields += " index={}".format(index)

            xml = "<{0}{2}>{1}</{0}>".format(
                tokenType, self.xmlProtect(tokenVal), fields
            )

        else:
            # If the XML starts with '</', reduce the indent level
            if xml[:2] == "</":
                self.indentLevel = self.indentLevel - 1

        # Output the XML, indented to the current level
        output = "{}{}\n".format(self.INDENT * self.indentLevel, xml)
        self.writer.writeComment(output)
        if self.DEBUG:
            print(output, end="")

        # If the XML does not contain '</', increase the indent level
        if "</" not in xml:
            self.indentLevel = self.indentLevel + 1

    def eatAndEmit(
        self, tokenType, tokenVals=None, category=None, state=None, varType=None
    ):
        """
        Shorthand for common pattern of eat and emit. Returns the token eaten.
        """
        token = self.eat(tokenType, tokenVals)
        self.emit(token=token, category=category, state=state, varType=varType)

        # Return the token in case the caller wants it
        return token

    def xmlProtect(self, token):
        # Protect <, >, and & tokens from XML
        if token == "<":
            return "&lt;"
        elif token == ">":
            return "&gt;"
        elif token == "&":
            return "&amp;"
        else:
            return token
