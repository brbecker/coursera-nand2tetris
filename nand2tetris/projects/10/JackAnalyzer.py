import sys, os, os.path
# import JackTokenizer
# import CompilationEngine

DEBUG = True

# Get Jack file or directory of files from the command line
try:
    arg  = sys.argv[1]
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
    # tokenizer = JackTokenizer(jackFile, DEBUG)

    xmlFile = os.path.basename(jackFile).replace(".jack", "T.xml")
    if DEBUG: print('jackFile: {:<30}xmlFile: {}'.format(jackFile, xmlFile))
