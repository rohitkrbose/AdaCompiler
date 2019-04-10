ST = None

class CodeGen:

	def __init__ (self):
		self.code = ''

	def getReg(self, selector, dtype): # 0 for operand 1 , 1 for operand 2, 2 for result
		reg = ('f' if dtype == 'Float' else 't') + str(selector)
		return reg

	def ac (self, s, tab = True):
		l = s + '\n'
		self.code = self.code + '\t' + l if tab == True else self.code + l

	def loadIntoReg (self, var, selector, dtype):
		if selector == 2: # For LHS
			return self.getReg(selector, dtype)
		elif selector == -1: # For syscalls
			if dtype == 'Float':
				reg = 'f12'
			else:
				reg = 'a0'
		else: # natural
			reg = self.getReg(selector, dtype)
		if isinstance(var, int): # integer constant
			self.ac('li $' + reg + ', ' + str(var) )
		elif isinstance(var, float): # float constant
			self.ac('li.s $' + reg + ', ' + str(var) )
		elif '[' in var: # array
			off  = (var.split('[')[1]).split(']')[0]
			var = var.split('[')[0]
			reg_off = self.getReg(off_var, 4, 'Integer')
			reg_var = self.getReg(var, 5, 'Integer')
			self.ac('li $' + reg_var + ', ' + str(ST.act_rec[var])) # Get offset of base address
			self.ac('add $' + reg_var + ', $sp, $', + reg_var) # Add it to stack pointer 
			self.ac('lw $' + reg_off + ', ' + str(ST.act_rec[off]) + '($sp)') # Get offset of index (probably in temp)
			self.ac('add $' + reg_var + ', ', reg_var, ', ', reg_off) # Add both offsets
			if dtype == 'Float':
				self.ac('l.s $' + reg + ', ($' + reg_var +')')
			elif dtype == 'Integer':
				self.ac('lw $' + reg + ', ($' + reg_var +')')
		else:
			if dtype == 'Float':
				self.ac('l.s $'+ reg + ', ' + str(ST.act_rec[var]) + '($sp)')
			elif dtype == 'Integer':
				self.ac('lw $'+ reg + ', ' + str(ST.act_rec[var]) + '($sp)')
		return reg

	def regToMem (self, reg, var, dtype):
		if '[' in var: # array
			off  = (var.split('[')[1]).split(']')[0]
			var = var.split('[')[0]
			reg_off = self.getReg(off_var, 4, 'Integer')
			reg_var = self.getReg(var, 5, 'Integer')
			self.ac('li $' + reg_var + ', ' + str(ST.act_rec[var])) # Get offset of base address
			self.ac('add $' + reg_var + ', $sp, $', + reg_var) # Add it to stack pointer 
			self.ac('lw $' + reg_off + ', ' + str(ST.act_rec[off]) + '($sp)') # Get offset of index (probably in temp)
			self.ac('add $' + reg_var + ', ', reg_var, ', ', reg_off) # Add both offsets
			if dtype == 'Float':
				self.ac('s.s $' + reg + ', ($' + reg_var +')')
			elif dtype == 'Integer':
				self.ac('sw $' + reg + ', ($' + reg_var +')')
		else:
			if dtype == 'Float':
				self.ac('s.s $'+ reg + ', ' + str(ST.act_rec[var]) + '($sp)')
			elif dtype == 'Integer':
				self.ac('sw $'+ reg + ', ' + str(ST.act_rec[var]) + '($sp)')

	def generateCode (self, symTab, instr_list, main_method):
		
		global ST
		ST = symTab.table[main_method]['ST']

		# DATA section

		self.ac('.data', False)
		self.ac('newline : .asciiz "\\n"', False)

		for instr in instr_list:
			l_no,op,lhs,op1,op2 = instr
			self.ac('L' + str(l_no) + ':', False)

			# Algebraic expression

			if op in ['+','-','*','/']:
				reg_lhs = self.loadIntoReg(lhs, 2, 'Integer')
				reg_op1 = self.loadIntoReg(op1, 0, 'Integer')
				reg_op2 = self.loadIntoReg(op2, 1, 'Integer')
				i = {'+':'add','-':'sub','*':'mul','/':'div'}[op]
				self.ac(i + ' $' + reg_lhs + ', $' + reg_op1 + ', $' + reg_op2)
				self.regToMem(reg_lhs,lhs,'Integer')
			elif op in ['+_float','-_float','*_float','/_float']:
				reg_lhs = self.loadIntoReg(lhs, 2, 'Float')
				reg_op1 = self.loadIntoReg(op1, 0, 'Float')
				reg_op2 = self.loadIntoReg(op2, 1, 'Float')
				i = {'+_float':'add.s','-_float':'sub.s','*_float':'mul.s','/_float':'div.s'}[op]
				self.ac(i + ' $' + reg_lhs + ', $' + reg_op1 + ', $' + reg_op2)
				self.regToMem(reg_lhs,lhs,'Float')

			# Assignment
			if op == '=':
				reg = self.loadIntoReg(op1, 0, 'Integer')
				self.regToMem(reg , lhs , 'Integer')
			elif op == '=_float':
				reg = self.loadIntoReg(op1, 0, 'Float')
				self.regToMem(reg , lhs , 'Float')

			# TypeCast
			if op == 'typecast':
				if op2 == 'Integer2Float':
					reg = self.loadIntoReg(op1, 8, 'Float')
					self.ac('cvt.s.w $f8, $f8')
					self.regToMem(reg, op1, 'Float')

			# Printing / Scanning
			if op == 'io':
				if lhs == 'print_int':
					self.ac('li $v0' + ', ' + '1')
					reg = self.loadIntoReg(op1, -1, 'Integer')
					self.ac('syscall')
				elif lhs == 'print_float':
					self.ac('li $v0' + ', ' + '2')
					reg = self.loadIntoReg(op1, -1, 'Float')
					self.ac('syscall')
				elif lhs == 'print_char':
					self.ac('li $v0' + ', ' + '11')
					reg = self.loadIntoReg(op1, -1, 'Integer')
					self.ac('syscall')
				elif lhs == 'scan_int':
					self.ac('li $v0' + ', ' + '5')
					self.ac('syscall')
					self.regToMem('v0', op1, 'Integer')
				elif lhs == 'scan_float':
					self.ac('li $v0' + ', ' + '6')
					self.ac('syscall')
					self.regToMem('f0', op1, 'Float')
				elif lhs == 'scan_char':
					self.ac('li $v0' + ', ' + '12')
					self.ac('syscall')
					self.regToMem('v0', op1, 'Integer')

		print (self.code)