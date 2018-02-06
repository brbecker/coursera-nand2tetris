from JackTokenizer import JackTokenizer

class CompilationEngine:
    """
    Effects the actual compilation output. Gets its input from a JackTokenizer
    and emits its parsed structure into an output file/stream.
    """

    def __init__(self, jackFile, xmlFile, DEBUG=False):
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass().
        """
        self.tokenizer = JackTokenizer(jackFile)
        self.xmlFile = open(xmlFile, mode='w')
        self.DEBUG = DEBUG

    def compileClass(self):
        """
        Compiles a complete class.
        """
        pass

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
