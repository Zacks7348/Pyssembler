.data
prompt: .asciiz "Enter name: "
new_line: .asciiz "\n"
name: .space 20

.text
main: li $v0, 4
la $a0, prompt
syscall # print str

li $v0, 8
la $a0, name # buffer to write to
li $a1, 20  # number of bytes for string

