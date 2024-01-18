.globl main

main: addiu $s1, $zero, 10
loop: add $s2, $s1, $s1
jal loop
