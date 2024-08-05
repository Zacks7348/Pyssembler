.globl main

main: addiu $s1, $zero, 10
addiu $s3, $zero, 100
loop: add $s2, $s2, $s1
# bne $s2, $s3, loop
jal main
