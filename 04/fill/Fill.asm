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

// Put your code here.
// currently no bounds checking for count (needed), maybe add later

(NOT-PRESSED)
	@count
	M=0
(NP-LOOP)
	@KBD
	D=M
	@PRESSED
	D;JNE

	@count
	D=M
	@SCREEN
	A=A+D
	M=0

	@count
	D=M
	D=D+1
	M=D

	@NP-LOOP
	0;JMP

(PRESSED)
	@count
	M=0
(P-LOOP)
	@KBD
	D=M
	@NOT-PRESSED
	D;JEQ

	@count
	D=M
	@SCREEN
	A=A+D
	M=-1

	@count
	D=M
	D=D+1
	M=D
	
	@P-LOOP
	0;JMP
