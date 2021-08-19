addiu $t1, $zero, 100
addiu $t2, $zero, -100
addiu $t3, $zero, 2147483640

add $s3, $t1, $t2
#addiupc $s4 100
addu $s5, $t3, $t1
#align $s6, $t1, $t2, 1
#aluipc $s7, 100
