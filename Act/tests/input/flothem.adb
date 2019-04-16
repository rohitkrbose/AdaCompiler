.data
	x: .word 0
	
.text
main:
	jal L1
	j L_end
L1:
	# Label_main_BEGIN:
	sw $fp, -4($sp)
	sw $ra, -8($sp)
	la $fp, 0($sp)
	la $sp, -32($sp)
L2:
	li.s $f0, 5.0
	s.s $f0, -16($sp)
L3:
	lw $t0, -16($sp)
	lw $t1, -16($sp)
	mul $t2, $t0, $t1
	sw $t2, -28($sp)
L4:
	lw $t0, -28($sp)
	li.s $t1, 2.3
	add $t2, $t0, $t1
	sw $t2, -32($sp)
L5:
	l.s $f0, -32($sp)
	s.s $f0, -24($sp)
L6:
	li $v0, 2
	l.s $f12, -24($sp)
	syscall
L7:
	la $sp, 0($fp)
	lw $ra, -8($sp)
	lw $fp, -4($sp)
	jr $ra
	# Label_main_END:
L8:
	jal L1
L_end:
	li $v0, 10
	syscall