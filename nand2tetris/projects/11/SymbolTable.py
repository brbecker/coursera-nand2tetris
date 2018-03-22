class SymbolTable():
    """
    Provides a symbol table abstraction. The symbol table associates the
    identifier names found in the program with identifier properties needed
    for compilation: type kind, and running index. The symbol table for Jack
    programs has two nested scopes (class/subroutine).
    """
    def __init__(self):
        """
        Creates a new, empty symbol table.
        """
        self.classTable = {}
        self.subroutineTable = {}

    def startSubroutine(self):
        """
        Starts a new subroutine scope (i.e., resets the subroutine's symbol
        table).
        """
        self.subroutineTable = {}

    def define(self, name, type, kind):
        """
        Defines a new identifier of a given name, type and kind and assigns it
        a running index. STATIC and FIELD identifiers have a class scope,
        while ARG and VAR identifiers have a subroutine scope.
        """
        pass

    def varCount(self, kind):
        """
        Returns the number of variables of the given kind already defined in
        the current scope.
        """
        pass

    def kindOf(self, name):
        """
        Returns the kind of the named identifier in the current scope. If the
        identifier is unknown in the current scope, returns None.
        """
        pass

    def typeOf(self, name):
        """
        Returns the type of the named identifier in the current scope.
        """
        pass

    def indexOf(self, name):
        """
        Returns the index assigned to the named identifier.
        """
        pass
