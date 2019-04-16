class ThreeAddrCode:

	def __init__ (self):
		self.code_list = []
		self.line_no = 1
		self.temp_count = 1

	def isDict(self, d):
		return (isinstance(d,dict))

	def emit (self, op1=None, op2=None, op=None, lhs=None):
		op1 = op1['tag'] if self.isDict(op1) else op1
		op2 = op2['tag'] if self.isDict(op2) else op2
		self.code_list.append([self.line_no,op,lhs,op1,op2])
		self.line_no += 1

	def newTemp (self, dtype, ST):
		var_name = '_temp' + str(self.temp_count)
		self.temp_count += 1
		attr_dict = {'what': 'var', 'type': dtype, 'tag': var_name, 'width': ST.getWidth(dtype)}
		ST.insert (var_name, attr_dict)
		return (var_name)

	def resetTemp (self, ST):
		# if doing this, erase all temporary variables from ST
		self.temp_count = 1
		for item in list(ST.table.keys()).copy():
			if (item[:5] == '_temp'):
				del ST.table[item]

	def getLine(self):
		return self.line_no

	def output (self):
		for line in self.code_list:
			print (line)

	def makeList (self, i):
		return ([i])

	def merge (self, p1, p2):
		return (p1+p2)

	def backpatch (self, p, i):
		for l in p:
			# print (self.code_list[l-1])
			assert self.code_list[l-1][1][:4] == 'goto'
			self.code_list[l-1][2] = i # line numbers are indexed from 1, LHS placeholder contains jump label