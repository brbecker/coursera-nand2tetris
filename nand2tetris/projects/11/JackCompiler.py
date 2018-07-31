import sys, os, os.path
from CompilationEngine import CompilationEngine

DEBUG = False

# Get Jack file or directory of files from the command line
try:
    arg = sys.argv[1]
except IndexError as e:
    print('Usage:JackAnalyzer.py file.jack|directory')
    sys.exit(1)

# If the argument has '.jack' in it, assume it's a file, otherwise a folder
jackFiles = []
if arg.endswith('.jack'):
    jackFiles.append(arg)
else:
    with os.scandir(arg) as it:
        for entry in it:
            if entry.name.endswith('.jack') and entry.is_file():
                jackFiles.append(os.path.join(arg, entry.name))
if DEBUG: print('jackFiles:\t' + str(jackFiles))

# Main Loop
for jackFile in jackFiles:
    # Generate the output VM file name
    xmlFile = jackFile.replace('.jack', '.xml')
    vmFile = jackFile.replace('.jack', '.vm')
    if DEBUG: print('jackFile: {:<30}xmlFile: {} vmFile: {}'.format(jackFile, xmlFile, vmFile))

    compEngine = CompilationEngine(jackFile=jackFile,
                                   xmlFile=xmlFile,
                                   vmFile=vmFile,
                                   DEBUG=DEBUG)
    compEngine.compileClass()

