class VMWriter:
    """
    Emits VM commands into a file, using the VM command syntax.
    """

    # Map Jack segment names to VM segment names.
    segments = {
        "ARG": "argument",
        "CONST": "constant",
        "FIELD": "this",
        "LOCAL": "local",
        "POINTER": "pointer",
        "STATIC": "static",
        "TEMP": "temp",
        "THAT": "that",
        "THIS": "this",
        "VAR": "local",
    }

    def __init__(self, vmFile, DEBUG=False):
        """
        Creates a new file and prepares it for writing.
        """
        self.DEBUG = DEBUG
        self.vmFile = vmFile
        self.file = open(self.vmFile, mode="w")

        if self.DEBUG:
            print("DEBUG(VMWriter): Opened {} for writing".format(self.vmFile))

    def writePush(self, segment, index):
        """
        Writes a VM push command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): push {} {}".format(segment, index))
        self.file.write("push {} {}\n".format(self.segments[segment], index))

    def writePop(self, segment, index):
        """
        Writes a VM pop command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): pop {} {}".format(segment, index))
        self.file.write("pop {} {}\n".format(self.segments[segment], index))

    def writeArithmetic(self, command):
        """
        Writes a VM arithmetic command.
        """
        # ['+', '-', '*', '/', '&', '|', '<', '>', '=', 'U-', 'U~']
        # U- and U~ are the unary operators.
        if self.DEBUG:
            print("DEBUG(VMWriter): arithmetic {}".format(command))

        if command == "+":
            self.file.write("add\n")
        elif command == "-":
            self.file.write("sub\n")
        elif command == "*":
            self.writeCall("Math.multiply", 2)
        elif command == "/":
            self.writeCall("Math.divide", 2)
        elif command == "&":
            self.file.write("and\n")
        elif command == "|":
            self.file.write("or\n")
        elif command == "<":
            self.file.write("lt\n")
        elif command == ">":
            self.file.write("gt\n")
        elif command == "=":
            self.file.write("eq\n")
        elif command == "U-":
            self.file.write("neg\n")
        elif command == "U~":
            self.file.write("not\n")
        else:
            raise NotImplementedError("Unrecognized arithmetic operator: " + command)

    def writeLabel(self, label):
        """
        Writes a VM label command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): label {}".format(label))

    def writeGoto(self, label):
        """
        Writes a VM goto command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): goto {}".format(label))

    def writeIf(self, label):
        """
        Writes a VM if-goto command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): if {}".format(label))

    def writeCall(self, name, nArgs):
        """
        Writes a VM call command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): call {} {}".format(name, nArgs))
        self.file.write("call {} {}\n".format(name, nArgs))

    def writeFunction(self, name, nLocals):
        """
        Writes a VM function command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): function {} {}".format(name, nLocals))
        self.file.write("function {} {}\n".format(name, nLocals))

    def writeReturn(self):
        """
        Writes a VM return command.
        """
        if self.DEBUG:
            print("DEBUG(VMWriter): return")
        self.file.write("return\n")

    def close(self):
        """
        Closes the output file
        """
        self.file.close()

        if self.DEBUG:
            print("DEBUG(VMWriter): Closed {}".format(self.vmFile))

    def writeComment(self, comment):
        """
        Writes a VM comment.
        """
        # if self.DEBUG:
        #     print('DEBUG(VMWriter): Writing comment \'{}\''.format(comment))
        self.file.write("// {}".format(comment))
