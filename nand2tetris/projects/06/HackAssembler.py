import sys,re
from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

# Set Filenames
asmfilename  = sys.argv[1]
hackfilename = asmfilename.replace(".asm", ".hack")

# Initialize symbol table
syms = SymbolTable()
syms.addEntry('SP', 0)
syms.addEntry('LCL', 1)
syms.addEntry('ARG', 2)
syms.addEntry('THIS', 3)
syms.addEntry('THAT', 4)
for i in range(16):
	syms.addEntry('R'+str(i), i)
syms.addEntry('SCREEN', 16384)
syms.addEntry('KBD', 24576)

# Pass 1 (define jump symbols only)
parser = Parser(asmfilename)
pc = 0
for junk in parser.advance():
	ctype = parser.commandType()
	if ctype == Parser.L_COMMAND:
		syms.addEntry(parser.symbol(), pc)
	else:
		pc = pc + 1

# Pass 2
parser = Parser(asmfilename)
hackfile = open(hackfilename, "w")
varloc = 16
for junk in parser.advance():
	ctype = parser.commandType()
	if ctype == Parser.A_COMMAND:
		sym = parser.symbol()
		if re.match('^[0-9]+$', sym):
			print('0{:015b}'.format(int(sym)), file=hackfile)
		else:
			if not syms.contains(sym):
				syms.addEntry(sym, varloc)
				varloc = varloc + 1
			print('0{:015b}'.format(syms.getAddress(sym)), file=hackfile)
	elif ctype == Parser.C_COMMAND:
		print('111' + Code.comp(parser.comp()) + 
			Code.dest(parser.dest()) + Code.jump(parser.jump()), file=hackfile)
