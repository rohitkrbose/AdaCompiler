ST = None

class CodeGen:

	def __init__ (self):
		self.code = ''

	def getReg(self, selector, dtype): # 0 for operand 1 , 1 for operand 2, 2 for result
		reg = ('f' if dtype == 'float' else 't') + str(selector)
		return reg

	def ac (self, s, tab = True):
		l = s + '\n'
		self.code = self.code + '\t' + l if tab == True else self.code + l

	def loadIntoReg (self, var, selector, dtype):
		if selector == 2: # For LHS
			return self.getReg(selector, dtype)
		elif selector == -2:
			if dtype == 'integer':
				reg = 'v0'
			elif dtype == 'float':
				reg = 'v1'
		elif selector == -1: # For syscalls
			if dtype == 'float':
				reg = 'f12'
			else:
				reg = 'a0'
		else: # natural
			reg = self.getReg(selector, dtype)
		if isinstance(var, int): # integer constant
			self.ac('li $' + reg + ', ' + str(var) )
		elif isinstance(var, float): # float constant
			self.ac('l.s $' + reg + ', ' + str(var) )
		elif '[' in var: # array
			off  = (var.split('[')[1]).split(']')[0]
			var = var.split('[')[0]
			reg_off = self.getReg( 4, 'integer')
			reg_var = self.getReg( 5, 'integer')
			self.ac('li $' + reg_var + ', ' + str(ST.act_rec[var])) # Get offset of base address
			self.ac('add $' + reg_var + ', $fp, $' + reg_var) # Add it to stack pointer 
			self.ac('lw $' + reg_off + ', ' + str(ST.act_rec[off]) + '($fp)') # Get offset of index (probably in temp)
			self.ac('add $' + reg_var + ', $' + reg_var + ', $' + reg_off) # Add both offsets
			if dtype == 'float':
				self.ac('l.s $' + reg + ', ($' + reg_var +')')
			elif dtype == 'integer':
				self.ac('lw $' + reg + ', ($' + reg_var +')')
		else:
			if dtype == 'float':
				self.ac('l.s $'+ reg + ', ' + str(ST.act_rec[var]) + '($fp)')
			elif dtype == 'integer':
				self.ac('lw $'+ reg + ', ' + str(ST.act_rec[var]) + '($fp)')
		return reg

	def regToMem (self, reg, var, dtype):
		if '[' in var: # array
			off  = (var.split('[')[1]).split(']')[0]
			# print('daaaaaaaaaa',ST.table[off])
			var = var.split('[')[0]
			reg_off = self.getReg( 4, 'integer')
			reg_var = self.getReg( 5, 'integer')
			self.ac('li $' + reg_var + ', ' + str(ST.act_rec[var])) # Get offset of base address
			self.ac('add $' + reg_var + ', $fp, $' + reg_var) # Add it to stack pointer 
			self.ac('lw $' + reg_off + ', ' + str(ST.act_rec[off]) + '($fp)') # Get offset of index (probably in temp)
			self.ac('add $' + reg_var + ', $' + reg_var + ', $' + reg_off) # Add both offsets
			if dtype == 'float':
				self.ac('s.s $' + reg + ', ($' + reg_var +')')
			elif dtype == 'integer':
				self.ac('sw $' + reg + ', ($' + reg_var +')')
		else:
			if dtype == 'float':
				self.ac('s.s $'+ reg + ', ' + str(ST.act_rec[var]) + '($fp)')
			elif dtype == 'integer':
				self.ac('sw $'+ reg + ', ' + str(ST.act_rec[var]) + '($fp)')

	def generateCode (self, symTab, instr_list, global_method):
		
		global ST
		Root_ST = symTab.table[global_method]['ST']
		ST = Root_ST

		# DATA section
		self.ac('.data', False)
		# Declare Global Variables
		for var in ST.table:
			if ST.table[var]['what'] == 'var':
				if ST.table[var]['type'] == 'integer':
					self.ac(var + ': .word 0')
				elif ST.table[var]['type'] == 'Character':
					self.ac(var + ': .byte 0')
				elif ST.table[var]['type'] == 'float':
					self.ac(var + ': .float 0')

		self.ac('')

		# ASCIIZ section
		# self.ac('newline : .asciiz "\\n"', False)

		# TEXT section
		self.ac('.text', False)

		self.ac('main:', False)
		self.ac('jal L' + str(Root_ST.table['main']['ST'].beginLine))
		self.ac('j L_end')

		for instr in instr_list:
			print (instr)
			l_no,op,lhs,op1,op2 = instr
			self.ac('L' + str(l_no) + ':', False)

			# Algebraic expression

			if op in ['+','-','*','/']:
				reg_lhs = self.loadIntoReg(lhs, 2, 'integer')
				reg_op1 = self.loadIntoReg(op1, 0, 'integer')
				reg_op2 = self.loadIntoReg(op2, 1, 'integer')
				i = {'+':'add','-':'sub','*':'mul','/':'div'}[op]
				self.ac(i + ' $' + reg_lhs + ', $' + reg_op1 + ', $' + reg_op2)
				self.regToMem(reg_lhs,lhs,'integer')
			elif op in ['+_float','-_float','*_float','/_float']:
				reg_lhs = self.loadIntoReg(lhs, 2, 'float')
				reg_op1 = self.loadIntoReg(op1, 0, 'float')
				reg_op2 = self.loadIntoReg(op2, 1, 'float')
				i = {'+_float':'add.s','-_float':'sub.s','*_float':'mul.s','/_float':'div.s'}[op]
				self.ac(i + ' $' + reg_lhs + ', $' + reg_op1 + ', $' + reg_op2)
				self.regToMem(reg_lhs,lhs,'float')

			# Assignment
			if op == '=':
				reg = self.loadIntoReg(op1, 0, 'integer')
				self.regToMem(reg , lhs , 'integer')
			elif op == '=_float':
				reg = self.loadIntoReg(op1, 0, 'float')
				self.regToMem(reg , lhs , 'float')
			elif op == '=_ptr':
				reg = self.loadIntoReg(op1, 0, '') ### where to load for pointers
				self.regToMem(reg , lhs , '')

			# TypeCast
			if op == 'typecast':
				if op2 == 'integer2float':
					reg_int = self.loadIntoReg(op1, 0, 'integer')
					self.ac('mtc1 $t0, $f0')
					self.ac('cvt.s.w $f0, $f0')
					self.regToMem('f0', lhs, 'float')

			# Printing / Scanning
			if op == 'io':
				if lhs == 'print_int':
					self.ac('li $v0' + ', ' + '1')
					reg = self.loadIntoReg(op1, -1, 'integer')
					self.ac('syscall')
				elif lhs == 'print_float':
					self.ac('li $v0' + ', ' + '2')
					reg = self.loadIntoReg(op1, -1, 'float')
					self.ac('syscall')
				elif lhs == 'print_char':
					self.ac('li $v0' + ', ' + '11')
					reg = self.loadIntoReg(op1, -1, 'integer')
					self.ac('syscall')
				elif lhs == 'scan_int':
					self.ac('li $v0' + ', ' + '5')
					self.ac('syscall')
					self.regToMem('v0', op1, 'integer')
				elif lhs == 'scan_float':
					self.ac('li $v0' + ', ' + '6')
					self.ac('syscall')
					self.regToMem('f0', op1, 'float')
				elif lhs == 'scan_char':
					self.ac('li $v0' + ', ' + '12')
					self.ac('syscall')
					self.regToMem('v0', op1, 'integer')

			# Parameter passing
			if op == 'param':
				# print (ST.table.keys())
				if isinstance(lhs, int):
					self.ac('li $t0, ' + str(lhs))
					self.ac('sw  $t0, -4($sp)') # Hardcode register
					self.ac('la $sp, -4($sp)')
				elif isinstance(lhs, float):
					self.ac('l.s $f0, ' + str(lhs))
					self.ac('s.s  $f0, -8($sp)') # Hardcode register
					self.ac('la $sp, -8($sp)')
				elif 'type' in ST.table[lhs] and ST.table[lhs]['type'] == 'integer':
					reg = self.loadIntoReg(lhs, 0, 'integer')
					self.ac('sw $' + reg + ', -4($sp)')
					self.ac('la $sp, -4($sp)')
				elif 'type' in ST.table[lhs] and ST.table[lhs]['type'] == 'float':
					reg = self.loadIntoReg(lhs, 0, 'float')
					self.ac('s.s $' + reg + ', -8($sp)')
					self.ac('la $sp, -8($sp)')
				elif ST.getAttrVal(ST.table[lhs]['type'], 'access'):
					self.ac('gambu')


			# procedure handling
			if op == 'label':
				if lhs[-6:] == '_BEGIN':
					self.ac('# Label_' + lhs + ':')
					proc_name = lhs[:-6] # Exclude _BEGIN
					ST = ST.table[proc_name]['ST']
					# print (ST.act_rec)
					self.ac('sw $fp, -4($sp)') # Store fp in sp[-4]
					self.ac('sw $ra, -8($sp)') # Store ra in sp[-8]
					self.ac('la $fp, 0($sp)') # Store sp[0] in fp
					self.ac('la $sp, -' + str(ST.neg_offset) + '($sp)') # local variables
					# print ('width = ', ST.neg_offset)
					# We can access fp easily.
					# self.ac('la $sp, -' + str(32 + ST.act_rec[proc_name]) + '($sp)')
				elif lhs[-4:] == '_END':
					proc_name = lhs[:-4] # Exclude _END
					ST = Root_ST # HACK
					if ST.table[proc_name]['what'] == 'procedure':
						self.ac('la $sp, 0($fp)')
						self.ac('lw $ra, -8($sp)')
						self.ac('lw $fp, -4($sp)')
						self.ac('jr $ra')
					self.ac('# Label_'+lhs+':')

			if op == 'return':
				if isinstance(op1, int):
					self.ac('li $v0, ' + str(op1))
				elif isinstance(op1, float):
					self.ac('li $v1, ' + str(op1))
				elif ST.table[op1]['type'] == 'integer':
					reg = self.loadIntoReg(op1, -2, 'integer')
				elif ST.table[op1]['type'] == 'float':
					reg = self.loadIntoReg(op1, -2, 'float')
				self.ac('la $sp, 0($fp)')
				self.ac('lw $ra, -8($sp)')
				self.ac('lw $fp, -4($sp)')
				self.ac('jr $ra')

			if op == 'call':
				param_count = int(op1)
				self.ac('jal ' + 'L' + str(Root_ST.table[lhs]['ST'].beginLine))
				self.ac('la $sp, ' + str(Root_ST.table[lhs]['ST'].pos_offset) + '($sp)')
				if op2 != None:
					if ST.table[op2]['type'] == 'integer':
						self.regToMem('v0', op2, 'integer')
					elif ST.table[op2]['type'] == 'float':
						self.regToMem('v1', op2, 'float')

			if op == 'goto':
				self.ac('j L' + str(lhs))

			# Unary handling
			if op[:3] == 'un_':
				if op == 'un_integer_-':
					reg_op1 = self.loadIntoReg(op1, 0, 'integer')
					self.ac('neg.s $' + reg_op1 + ', $' + reg_op1)
					self.regToMem(reg_op1, op2, 'integer')
				elif op == 'un_float_-':
					reg_op1 = self.loadIntoReg(op1, 0, 'float')
					self.ac('neg.s $' + reg_op1 + ', $' + reg_op1)
					self.regToMem(reg_op1, op2, 'float')
				elif op == 'un_integer_+':
					reg_op1 = self.loadIntoReg(op1, 0, 'integer')
					self.regToMem(reg_op1, op2, 'integer')
				elif op == 'un_float_+':
					reg_op1 = self.loadIntoReg(op1, 0, 'float')
					self.regToMem(reg_op1, op2, 'float')

			# and and or
			if op == 'and':
				reg_lhs = self.loadIntoReg(lhs, 2, 'integer')
				reg_op1 = self.loadIntoReg(op1, 0, 'integer')
				reg_op2 = self.loadIntoReg(op2, 1, 'integer')
				#why  ?
				self.ac('and $' + reg_lhs + ', $' + reg_op1 + ', $' + reg_op2)
				regToMem(reg_lhs, lhs, 'integer')

			if op == 'or':
				reg_lhs = self.loadIntoReg(lhs, 2, 'integer')
				reg_op1 = self.loadIntoReg(op1, 0, 'integer')
				reg_op2 = self.loadIntoReg(op2, 1, 'integer')
				self.ac('or $' + reg_lhs + ', $' + reg_op1 + ', $' + reg_op2)
				regToMem(reg_lhs, lhs, 'integer')

			# comparison operators
			if len(op.split("_")) >= 2 and op.split("_")[1] in ['/=','=','>','<','<=','>=']:  
				typ = op.split("_")[2]
				sym = op.split("_")[1]

				if typ == 'float':
					reg_lhs = self.loadIntoReg(lhs, 2, 'integer')
					reg_op1 = self.loadIntoReg(op1, 0, 'float')
					reg_op2 = self.loadIntoReg(op2, 1, 'float')
				elif typ == 'integer':
					reg_lhs = self.loadIntoReg(lhs, 2, 'integer')
					reg_op1 = self.loadIntoReg(op1, 0, 'integer')
					reg_op2 = self.loadIntoReg(op2, 1, 'integer')
				else:
					if op2 == 'null':
						reg_lhs = self.loadIntoReg(lhs, 2, 'integer')
						reg_op1 = self.loadIntoReg(op1, 0, 'integer')
						reg_op2 = self.loadIntoReg(0, 1, 'integer') # NULL pointer

				if typ == 'integer':
					if sym == '/=':
						ins = 'bne'
					elif sym == '=':
						ins = 'beq'
					elif sym == '>':
						ins = 'bgt'
					elif sym == '<':
						ins = 'blt'
					elif sym == '<=':
						ins = 'ble'
					elif sym == '>=':
						ins = 'bge'
					self.ac(ins +' $' + reg_op1 + ', $' + reg_op2 + ', L' + str(lhs))
				elif typ == 'float':
					if sym == '/=':
						ins = 'c.ne.s'
					elif sym == '=':
						ins = 'c.eq.s'
					elif sym == '>':
						ins = 'c.gt.s'
					elif sym == '<':
						ins = 'c.lt.s'
					elif sym == '<=':
						ins = 'c.le.s'
					elif sym == '>=':
						ins = 'c.ge.s'
					self.ac(ins + ' $' + reg_op1 + ', $' + reg_op2)
					self.ac('bc1t' + ' L' + str(lhs))


		self.ac('L_end:', False)
		self.ac('li $v0, 10') # Dummy statement
		self.ac('syscall')
				# print (instr)
				# print (',zuasd ', reg_lhs, lhs)
				# self.regToMem(reg_lhs, lhs, 'integer')

				
		print (self.code)