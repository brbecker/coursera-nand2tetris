import sys,os
from Parser import Parser
from CodeWriter import CodeWriter

DEBUG = False

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

        # Get the command type
        ctype = parser.commandType()

        # Generate the code for the command
        if ctype == Parser.C_ARITHMETIC:
            cw.writeArithmetic(parser.arg1(),
                               parser.command(), parser.lineno())
        elif ctype == Parser.C_PUSH or ctype == Parser.C_POP:
            cw.writePushPop(ctype, parser.arg1(), parser.arg2(),
                            parser.command(), parser.lineno())
        elif ctype in range(len(Parser.CMDS)):
            print("WARNING: Unimplemented ctype: " + ctype)
        else:
            print("ERROR: Unrecognized ctype: " + ctype)
            sys.exit(1)

# Close the CodeWriter
cw.close()
