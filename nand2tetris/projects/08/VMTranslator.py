import sys,os
from Parser import Parser
from CodeWriter import CodeWriter

DEBUG = True

# Get VM file or directory of files from the command line
try:
    arg  = sys.argv[1]
except IndexError as e:
    print('Usage: VMTranslator file.vm|directory')
    sys.exit(1)

# If the argument has '.vm' in it, assume it's a file, otherwise a folder
vmfiles = []
if arg.endswith('.vm'):
    vmfiles.append(arg)
    asmfilename = arg.replace(".vm", ".asm")
else:
    with os.scandir(arg) as it:
        for entry in it:
            if entry.name.endswith('.vm') and entry.is_file():
                vmfiles.append(os.path.join(arg, entry.name))
    asmfilename = arg + '.asm'

# print('vmfiles:\t' + str(vmfiles))
# print('asmfilename:\t' + asmfilename)

# Main Loop
cw = CodeWriter(asmfilename, DEBUG)
for vmfile in vmfiles:
    parser = Parser(vmfile, DEBUG)
    cw.setFileName(vmfile)
    # print('Parsing ' + vmfile + ' to ' + asmfilename)

    while parser.hasMoreCommands():
        # Read the next command
        parser.advance()

        # Get the command type and arguments
        ctype = parser.commandType()
        arg1  = parser.arg1()
        arg2  = parser.arg2()

        # Write a comment into the ASM file with the VM command
        cw.writeComment(parser.command(), parser.lineno())

        # Generate the code for the command
        if ctype == Parser.C_ARITHMETIC:
            cw.writeArithmetic(arg1, parser.lineno())
        elif ctype == Parser.C_PUSH or ctype == Parser.C_POP:
            cw.writePushPop(ctype, arg1, arg2)
        elif ctype == Parser.C_LABEL:
            cw.writeLabel(arg1)
        elif ctype == Parser.C_GOTO:
            cw.writeGoto(arg1)
        elif ctype == Parser.C_IF:
            cw.writeIf(arg1)
        elif ctype == Parser.C_FUNCTION:
            cw.writeFunction(arg1, arg2)
        elif ctype == Parser.C_RETURN:
            cw.writeReturn()
        elif ctype in range(len(Parser.CMDS)):
            print("WARNING: Unimplemented ctype: " + str(ctype))
        else:
            print("ERROR: Unrecognized ctype: " + str(ctype))
            sys.exit(1)

        # Write a blank line into the ASM file after each VM command
        cw.writeBlank()

# Close the CodeWriter
cw.close()
