class SymbolTable:
    """
    Provides a symbol table abstraction. The symbol table associates the
    identifier names found in the program with identifier properties needed
    for compilation: type kind, and running index. The symbol table for Jack
    programs has two nested scopes (class/subroutine).
    """

    # classTable has this structure:
    #   classTable[NAME] = (TYPE, KIND, INDEX)
    # subroutineTable is identical.

    def __init__(self, DEBUG=False):
        """
        Creates a new, empty symbol table.
        """
        self.DEBUG = DEBUG

        self.classTable = {}
        self.subroutineTable = {}

        self.counts = {}
        self.counts["STATIC"] = 0
        self.counts["FIELD"] = 0
        self.counts["ARG"] = 0
        self.counts["VAR"] = 0

        if self.DEBUG:
            print("DEBUG(SymbolTable): INITIALIZED SYMBOL TABLES")

    def startSubroutine(self):
        """
        Starts a new subroutine scope (i.e., resets the subroutine's symbol
        table).
        """
        self.subroutineTable = {}
        self.counts["ARG"] = 0
        self.counts["VAR"] = 0

        if self.DEBUG:
            print("DEBUG(SymbolTable): Reset subroutine symbol table")

    def define(self, aName, aType, aKind):
        """
        Defines a new identifier of a given name, type and kind and assigns it
        a running index. STATIC and FIELD identifiers have a class scope,
        while ARG and VAR identifiers have a subroutine scope.
        """
        if aKind in ["STATIC", "FIELD"]:
            table = self.classTable
        elif aKind in ["ARG", "VAR"]:
            table = self.subroutineTable
        else:
            raise ValueError("Unknown KIND: " + aKind)

        index = self.counts[aKind]
        table[aName] = (aType, aKind, index)
        if self.DEBUG:
            print(
                "DEBUG(SymbolTable): DEFINED SYMBOL '{}': {}".format(
                    aName, table[aName]
                )
            )
        self.counts[aKind] += 1

        # Return the index
        return index

    def varCount(self, aKind):
        """
        Returns the number of variables of the given kind already defined in
        the current scope.
        """
        return self.counts[aKind]

    def kindOf(self, aName):
        """
        Returns the kind of the named identifier in the current scope. If the
        identifier is unknown in the current scope, returns None.
        """
        if aName in self.subroutineTable:
            tup = self.subroutineTable[aName]
        elif aName in self.classTable:
            tup = self.classTable[aName]
        else:
            return None

        # DEBUG
        if self.DEBUG:
            print("DEBUG(SymbolTable): KIND OF '{}': {}".format(aName, tup[1]))

        # Extract the kind from the tuple
        return tup[1]

    def typeOf(self, aName):
        """
        Returns the type of the named identifier in the current scope. If the
        identifier is unknown in the current scope, returns None.
        """
        if aName in self.subroutineTable:
            tup = self.subroutineTable[aName]
        elif aName in self.classTable:
            tup = self.classTable[aName]
        else:
            return None

        # DEBUG
        if self.DEBUG:
            print("DEBUG(SymbolTable): TYPE OF '{}': {}".format(aName, tup[0]))

        # Extract the type from the tuple
        return tup[0]

    def indexOf(self, aName):
        """
        Returns the index assigned to the named identifier. If the identifier
        is unknown in the current scope, returns None.
        """
        if aName in self.subroutineTable:
            tup = self.subroutineTable[aName]
        elif aName in self.classTable:
            tup = self.classTable[aName]
        else:
            return None

        # DEBUG
        if self.DEBUG:
            print("DEBUG(SymbolTable): INDEX OF '{}': {}".format(aName, tup[2]))

        # Extract the index from the tuple
        return tup[2]
