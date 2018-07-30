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
    # Generate the output XML file name
    xmlFile = jackFile.replace(".jack", ".xml")
    if DEBUG: print('jackFile: {:<30}xmlFile: {}'.format(jackFile, xmlFile))

    compEngine = CompilationEngine(jackFile, xmlFile, DEBUG)
    compEngine.compileClass()

    # tokenizer = JackTokenizer(jackFile)#, xmlFile, DEBUG)

    # while tokenizer.hasMoreTokens():
    #     tokenizer.advance()
    #     tokenType = tokenizer.tokenType()
    #     if tokenType == JackTokenizer.KEYWORD:
    #         tokenVal = tokenizer.keyWord()
    #     elif tokenType == JackTokenizer.SYMBOL:
    #         tokenVal = tokenizer.symbol()
    #     elif tokenType == JackTokenizer.IDENTIFIER:
    #         tokenVal = tokenizer.identifier()
    #     elif tokenType == JackTokenizer.INT_CONST:
    #         tokenVal = tokenizer.intVal()
    #     elif tokenType == JackTokenizer.STRING_CONST:
    #         tokenVal = tokenizer.stringVal()
