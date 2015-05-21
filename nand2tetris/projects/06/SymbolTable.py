class SymbolTable:

	def __init__(self):
		self._syms = {}

	def addEntry(self, k, v):
		self._syms[k] = v

	def contains(self, k):
		return k in self._syms

	def getAddress(self, k):
		return self._syms[k]
