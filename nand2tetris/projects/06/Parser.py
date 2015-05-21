import re,sys

class Parser:

	# Command types
	(A_COMMAND, C_COMMAND, L_COMMAND) = range(3)

	# Regular expressions (compiled for speed)
	COMMENT_PATTERN   = re.compile(r'//.*$')
	A_COMMAND_PATTERN = re.compile(r'^@(.*)$')
	C_COMMAND_PATTERN = re.compile(r'^((A?M?D?)=)?' +
		r'(0|[ADM]?-?1|[-!]?[ADM]|[ADM]\+1|D[-+|&][AM]|[AM]-D)' +
		r'(;(J(EQ|NE|MP|[GL][ET])))?$')
	L_COMMAND_PATTERN = re.compile(r'^\((.*)\)$')

	def __init__(self, filename):
		# Initialize the Parser
		self._filename = filename
		self._hasMoreCommands = None

	def hasMoreCommands(self):
		return self.hasMoreCommands

	# This method reads forward in the file, skipping whitespace and comments,
	# until a command is found. Sets hasMoreCommands and commandType
	# appropriately.
	# Returns: None
	def advance(self):
		self._hasMoreCommands = True
		for line in open(self._filename):
			# Strip comments and whitespace
			line = Parser.COMMENT_PATTERN.sub('', line).strip()
			if len(line) > 0:
				#print(line + ' '*(24-len(line)), end='')
				# Parse the line
				self._symbol = self._dest = self._comp = self._jump = None
				# Look for A commands
				aMatch = Parser.A_COMMAND_PATTERN.match(line)
				if aMatch:
					self._commandType = Parser.A_COMMAND
					# Group 1 has address
					#print(str(aMatch.groups()))
					self._symbol = aMatch.group(1)
				else:
					# Look for C commands
					cMatch = Parser.C_COMMAND_PATTERN.match(line)
					if cMatch:
						self._commandType = Parser.C_COMMAND
						#print(str(cMatch.groups()))
						# Group 2 has dest, 3 has comp, 5 has jump
						self._dest = cMatch.group(2)
						self._comp = cMatch.group(3)
						self._jump = cMatch.group(5)
					else:
						# Look for labels
						lMatch = Parser.L_COMMAND_PATTERN.match(line)
						if lMatch:
							self._commandType = Parser.L_COMMAND
							#print(str(lMatch.groups()))
							# Group 1 has symbol
							self._symbol = lMatch.group(1)

				# If a command was found, yield control
				if aMatch or cMatch or lMatch:
					yield None
				else:
					print("Unrecognized: " + line)

		# No more commands
		self._hasMoreCommands = False


	def commandType(self):
		return self._commandType

	def symbol(self):
		return self._symbol

	def dest(self):
		return self._dest

	def comp(self):
		return self._comp

	def jump(self):
		return self._jump

if __name__ == '__main__':
	# self-test code
	test = Parser(sys.argv[1])
	for junk in test.advance():
		ctype = test.commandType()
		if ctype == Parser.A_COMMAND:
			print('A:\t' + test.symbol())
		elif ctype == Parser.C_COMMAND:
			print('C:\t' + str(test.dest()) + '\t' + test.comp() + '\t' + str(test.jump()))
		elif ctype == Parser.L_COMMAND:
			print('L:\t' + test.symbol())
