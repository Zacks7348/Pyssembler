.data
prompt: .asciiz "Enter Age: "
newline: .asciiz "\n"

.text
main: li $v0, 4
la $a0, prompt
syscall # print str

li $v0, 5
syscall # read int into $v0
move $t0, $v0 # move int to $t0

li $v0, 4
la $a0, newline
syscall # print str

li $v0, 1
move $a0, $t0 # move $v0 to $a0
syscall # print int
