.data
strings: .ascii "Hello World! "
.ascii "My Name is Zack. "
.asciiz "What is your name?"

.text
main: li $v0, 4
la $a0, strings
syscall