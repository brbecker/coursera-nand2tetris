import sys,os,re
from Parser import Parser
from CodeWriter import CodeWriter

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

print('vmfiles:\t' + str(vmfiles))
print('asmfilename:\t' + asmfilename)
