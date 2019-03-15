# function: tag, what, return type, parameter_count, parameter_types
# procedure: same as function except return type
# variable: tag, what, type, value
# types: tag, what, width

# If record needs to be copied, rec a = rec b, copy all variables in both one by one. Record variables
# are stored as <record_name>.<var_name>

import csv

Z = {}
U = []

class SymbolTable:

	def __init__ (self, parentTable = None):
		self.parentTable = parentTable
		if parentTable == None :
			self.table = {'Integer': {'tag': 'Integer', 'what': 'type', 'width': 4},
						'Float': {'tag': 'Float', 'what': 'type', 'width': 8},
						'print': {'tag': 'print', 'what': 'default_function'},
						'scan' : {'tag': 'scan', 'what': 'default_function'},
						'Ada.Text_IO' : {'tag': 'Ada.Text_IO', 'what': 'default_lib'},
						'Ada.Gnat_IO' : {'tag': 'Ada.Gnat_IO', 'what': 'default_lib'},
						'Ada.Integer_Text_IO': {'tag': 'Ada.Integer_Text_IO', 'what': 'default_lib'}	}
		else:
			self.table = {}

	def insert (self, var, attr_dict):
		if var in self.table:
			print ('ERROR: Entity already exists')
			return False
		self.table[var] = {}
		for attr in attr_dict:
			self.table[var][attr] = attr_dict[attr]
		return True

	def update (self, var, attr, val):
		currTable = self
		while (currTable != None):
			if var not in currTable.table:
				currTable = currTable.parentTable
			else:
				currTable.table[var][attr] = val
				return True
		print ('ERROR: Update. Entity does not exist.')
		return False

	def getAttrVal (self, var, attr):
		currTable = self
		while (currTable != None):
			if var not in currTable.table:
				currTable = currTable.parentTable
			else:
				return currTable.table[var][attr]
		print ('ERROR: GetAttrVal.', var, 'does not exist.')
		return None

	def getAttrDict (self, var):
		currTable = self
		while (currTable != None):
			if var not in currTable.table:
				currTable = currTable.parentTable
			else:
				return currTable.table[var]
		print ('ERROR: GetAttrDict.', var, 'does not exist.')
		return None

	def getWidth (self, dtype):
		currTable = self
		while (currTable != None):
			for k in currTable.table:
				if (currTable.table[k]['what'] == 'type' and currTable.table[k]['tag'] == dtype):
					return (currTable.table[k]['width'])
			currTable = currTable.parentTable
		return (None)

	def doesExist (self, var):
		currTable = self
		while (currTable != None):
			if (var in currTable.table):
				return True
			else:
				currTable = currTable.parentTable
		return False

# parameter pass by reference may need to be handled differently

	def spDeclare (self, var, attr_dict):
		if var in self.parentTable.table:
			print (var, 'ERROR: Entity already exists')
			return False
		else:
			self.parentTable.insert(var, attr_dict)
			for item in attr_dict['params']:
				self.insert(item['name'], item['attr_dict'])
			return True

	def beginScope (self):
		newTable = SymbolTable(self)
		return (newTable)

	def endScope (self):
		return (self.parentTable)

	def printTable (self):
		prop_list = ['tag','type','width','what','param_dict']
		for k in self.table:
			Z[k] = {}
			for j in self.table[k]:
				if j in prop_list:
					Z[k][j] = str(self.table[k][j])

	def dumpTable (self):
		prop_list = ['tag','type','width','what','param_dict']
		for k in Z:
			U.append(Z[k])
		with open('../output/SymTab_dump.csv', 'w') as output_file:
			dict_writer = csv.DictWriter(output_file, prop_list)
			dict_writer.writeheader()
			dict_writer.writerows(U)