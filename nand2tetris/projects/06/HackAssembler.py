import sys,re
from Parser import Parser
from Code import Code

asmfilename  = sys.argv[1]
hackfilename = asmfilename.replace(".asm", ".hack")

# Pass 2
parser = Parser(asmfilename)
hackfile = open(hackfilename, "w")
for junk in parser.advance():
	ctype = parser.commandType()
	if ctype == Parser.A_COMMAND:
		if re.match('^[0-9]+$', parser.symbol()):
			print('0{:015b}'.format(int(parser.symbol())), file=hackfile)
		else:
			pass
	elif ctype == Parser.C_COMMAND:
		print('111' + Code.comp(parser.comp()) + 
			Code.dest(parser.dest()) + Code.jump(parser.jump()), file=hackfile)
