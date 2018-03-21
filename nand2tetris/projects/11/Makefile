ANALYZER_SCRIPTS = JackAnalyzer.py JackTokenizer.py
TEXT_COMPARER = ..\..\tools\TextComparer.bat

ARRAYTEST_FILES = ArrayTest/Main.jack
SQUARE_FILES = Square/Main.jack \
	Square/Square.jack \
	Square/SquareGame.jack
SQUARE_NOEXP_FILES = ExpressionlessSquare/Main.jack \
	ExpressionlessSquare/Square.jack \
	ExpressionlessSquare/SquareGame.jack

ARRAYTEST_XML_FILES = ArrayTest/Main.Txml
SQUARE_XML_FILES = Square/Main.Txml \
	Square/Square.Txml \
	Square/SquareGame.Txml
SQUARE_NOEXP_XML_FILES = ExpressionlessSquare/Main.Txml \
	ExpressionlessSquare/Square.Txml \
	ExpressionlessSquare/SquareGame.Txml

%.Txml: %.jack
	python ./JackAnalyzer.py $<
	$(TEXT_COMPARER) $@.cmp $@

tokenizerTest: $(ANALYZER_SCRIPTS) $(ARRAYTEST_XML_FILES) $(SQUARE_XML_FILES) $(SQUARE_NOEXP_XML_FILES)
