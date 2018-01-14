// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// R2 = 0 // Set R2 to zero
	@R2
	M=0

// ctr = R1 // Copy R1 to be our counter
	@R1
	D=M
	@ctr
	M=D

// while (ctr > 0) // Jump to END if ctr (already in D) is zero
(LOOP)
	@END
	D;JEQ

// Add R0 to R2
	@R0
	D=M
	@R2
	M=D+M

// Decrement ctr (and load ctr into D)
	@ctr
	MD=M-1

// Set address to jump to top of loop
	@LOOP
// Either jump to top of loop or stay here infinitely
(END)
	0;JMP
