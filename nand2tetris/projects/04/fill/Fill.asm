// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(START)
// Initialize ptr to the start of the SCREEN
	@SCREEN
	D=A
	@ptr
	M=D

(LOOP)
// Load D with -1 if KBD non-zero or 0 if KBD zero
	@KBD
	D=M
	@ZERO
	D;JEQ
	D=-1
(ZERO)

// Write value of D to current screen location
	@ptr
	A=M
	M=D

// Increment pointer (and store in D)
	@ptr
	MD=M+1

// Compare D to KBD (which is end of SCREEN). If zero, go to START, else LOOP
	@KBD
	D=D-A
	@START
	D;JEQ
	@LOOP
	0;JMP
