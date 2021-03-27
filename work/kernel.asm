        .kdata
#Reserve space in kernel memory to save registers to
save1:  .word 0
save2:  .word 0

# Exception address for MIPS32
        .ktext 0x80000180
        add $k1, $at, $zero     #save $at
        sw $v0 save1
        sw $a0 save2

        mfc0 $k0 $13            # Move value in Cause register to k0
        srl $a0 $k0 2           # Get ExcCode 
        andi $a0 $a0 31 

# Print exception info
        li $v0 4                # set service code to 4 (print_str)
        la $a0



.text  
    .globl __start

__start:
	jal main                # start user program
	nop

	li $v0 10               # set service code to 10
	syscall			# syscall (code=10) exit
