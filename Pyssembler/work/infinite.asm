.data
s1: .asciiz "$s1="
nl: .asciiz "\n"

.text
main: 
	li $s2, 1000
loop: 	addiu $s1, $s1, 1

# print "$s1="
	li $v0, 4
	la $a0, s1
	syscall # print string

# print value in $s1
	li $v0, 1
	move $a0, $s1
	syscall # print int

# print newline
	li $v0, 4
	la $a0 nl
	syscall
	tge $s1, $s2 # trap when $s1 is greater than 1000
	j loop