# http://www.adaic.org/resources/add_content/standards/95lrm/grammar9x.y
# TO DO... switch statement

import sys, re, os, logging
from ply import lex, yacc
from copy import *
from Tokens import *

from symtab import SymbolTable
from ThreeAddrCode import ThreeAddrCode

err = False

ST = SymbolTable()
TAC = ThreeAddrCode()

def p_goal_symbol(p):
	'''goal_symbol : compilation
	'''
	global err
	ST.printTable()
	ST.dumpTable()
	if (err == False):
		TAC.output()	

def p_pragma(p):
	'''pragma : PRAGMA IDENTIFIER ';'
	   | PRAGMA simple_name '(' pragma_arg_s ')' ';'
	'''

def p_pragma_arg_s(p):
	'''pragma_arg_s : pragma_arg
	   | pragma_arg_s ',' pragma_arg
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_pragma_arg(p):
	'''pragma_arg : simple_expression
	   | simple_name ARROW simple_expression
	'''	

def p_pragma_s(p):
	'''pragma_s :
	   | pragma_s pragma
	'''

def p_decl(p):
	'''decl : object_decl
	   | record_decl
	   | subprog_decl
	   | lambda_decl
	'''
	p[0] = deepcopy(p[1])

def p_object_decl(p):
	'''object_decl : def_id_s ':' object_type_def ';'   
	'''
	if p[3] == None:
		print("ERROR: Object type unspecified!")
		p_error(p)
	else:	
		def_id_s = p[1]
		for idx in def_id_s:
			if idx in reserved:
				print("ERROR: Identifier is reserved !")
				p_error(p)
				continue
			if ST.doesExist(idx):
				print("ERROR: Identifier already declared !")
				p_error(p)
				continue
			if (p[3]['what'] == 'array'):
				attr_dict = deepcopy(p[3])
				attr_dict['tag'] = idx
				ST.insert (idx, attr_dict)
			elif (p[3]['what'] == 'record_type'):
				attr_dict = {'what': 'record', 'type': p[3]['tag']}
				ST.insert(idx, attr_dict)
				for k,v in p[3].items():
					if (k not in ['what','tag']): 
						idx_n = idx + '.' + k
						attr_dict = deepcopy(v)
						attr_dict['tag'] = idx_n
						ST.insert(idx_n, attr_dict)
			else:
				dtype = p[3]['tag']
				attr_dict = {'tag': idx, 'what': 'var', 'type': dtype}
				ST.insert(idx, attr_dict)

def p_def_id_s(p):
	'''def_id_s : def_id
	   | def_id_s ',' def_id
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_def_id(p):
	'''def_id  : IDENTIFIER
	'''
	p[0] = deepcopy(p[1])

def p_object_type_def(p):
	'''object_type_def : type_ind
	   | array_type
	'''
	p[0] = deepcopy(p[1])

def p_record_decl(p):
	'''record_decl : TYPE IDENTIFIER IS record_def ';'
	'''
	if ST.doesExist(p[2]):
		print("ERROR: Identifier already declared !")
		p_error(p)
	elif p[2] in reserved:
		print("ERROR: Identifier is reserved !")
		p_error(p)
	else:
		attr_dict = deepcopy(p[4])
		attr_dict['tag'] = p[2]
		attr_dict['what'] = 'record_type'
		ST.insert(p[2],attr_dict)
		p[0] = ST.getAttrDict(p[2])		

def p_type_ind(p):
	'''type_ind : name
	'''
	p[0] = deepcopy(p[1])

def p_range(p):
	'''range : simple_expression DOTDOT simple_expression
	'''
	if(p[1]['type'] != p[3]['type']):
		print('ERROR: range type mismatch !')
		p_error(p)
	else:	
		r_start = p[1]['tag'] if TAC.isDict(p[1]) else p[1]
		r_end = p[3]['tag'] if TAC.isDict(p[3]) else p[3]
		p[0] = {'r_start': r_start, 'r_end': r_end}
	
def p_array_type(p):
	'''array_type : ARRAY iter_index_constraint OF type_ind
	'''
	b_type = p[4]['tag']
	p[0] = {'r_start_s': [], 'r_end_s': [], 'what': 'array', 'type': b_type}
	ranges = p[2] # for multi-dim arrays
	count = 1
	for r in ranges:
		p[0]['r_start_s'].append(r['r_start'])
		p[0]['r_end_s'].append(r['r_end'])
		count *= r['r_end'] - r['r_start'] + 1
	p[0]['width'] = count * ST.getWidth(b_type)

def p_iter_index_constraint(p):
	'''iter_index_constraint : '(' range_s ')'
	'''
	p[0] = deepcopy(p[2])
	
def p_range_s(p):
	'''range_s : range
	   | range_s ',' range
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]
	
def p_record_def(p):
	'''record_def : RECORD param_s ';' END RECORD
	'''
	p[0] = deepcopy(p[2])

def p_decl_part(p):
	'''decl_part :
	   | decl_item_or_body_s
	'''

def p_decl_item(p):
	'''decl_item : decl
	   | use_clause
	   | pragma
	'''
	p[0] = deepcopy(p[1])

def p_decl_item_or_body_s(p):
	'''decl_item_or_body_s : decl_item_or_body
	   | decl_item_or_body_s decl_item_or_body
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
	
def p_decl_item_or_body(p):
	'''decl_item_or_body : body
	   | decl_item
	'''
	p[0] = deepcopy(p[1])
	
def p_body(p):
	'''body : subprog_body
	'''
	p[0] = deepcopy(p[1])

# assumes that this identifier has been seen previously
def p_name(p):
	'''name : compound_name
	   | indexed_comp
	'''
	if not isinstance(p[1], dict):
		p[0] = ST.getAttrDict(p[1])
	else:
		p[0] = deepcopy(p[1])
	
def p_mark(p):
	'''mark : name
	'''
	p[0] = deepcopy(p[1])

def p_simple_name(p):
	'''simple_name : IDENTIFIER
	'''
	p[0] = p[1]

def p_compound_name(p):
	'''compound_name : simple_name
	   | compound_name '.' simple_name
	'''
	if (len(p) == 2):
		p[0] = p[1]
	else:
		p[0] = p[1] + '.' + p[3]
	
def p_c_name_list(p):
	'''c_name_list : compound_name
	    | c_name_list ',' compound_name
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_indexed_comp(p):
	'''indexed_comp : name '(' value_s ')'
		| name '(' STRING ')'
	'''

	p[0] = deepcopy(p[1])
	if (p[1]['what'] == 'array'):
		if len(p[3]) != len(ST.getAttrVal(p[1]['tag'],'r_end_s')) :
			print('ERROR: Number of dimensions entered incorrectly !')
			p_error(p)
		else:
			for i,x in enumerate(p[3]):
				if x['type'] != 'Integer' :
					print('ERROR: Array Index not of Integer type !')
					p_error(p)
					return						
			array_dims = [x-y+1 for x,y in zip(p[1]['r_end_s'],p[1]['r_start_s'])]
			ind_s = p[3]
			dim = len(ind_s)
			off = 0
			tp = None
			for d in range (dim-1):
				t1 = TAC.newTemp('Integer', ST)
				t2 = TAC.newTemp('Integer', ST)
				TAC.emit(op='-',lhs=t1,op1=p[3][d],op2=p[1]['r_start_s'][d])
				TAC.emit(op='*',lhs=t2,op1=t1,op2=array_dims[d])
				if(tp==None):
					tp = t2
				else:
					t3 = TAC.newTemp('Integer',ST)
					TAC.emit(op='+',lhs=t3,op1=t2,op2=tp)
					tp = t3
			if (tp == None):
				t5 = TAC.newTemp('Integer',ST)
				TAC.emit(op='-',lhs=t5,op1=p[3][dim-1],op2=p[1]['r_start_s'][dim-1])
			else:
				t4 = TAC.newTemp('Integer',ST)
				TAC.emit(op='-',lhs=t4,op1=p[3][dim-1],op2=p[1]['r_start_s'][dim-1])
				t5 = TAC.newTemp('Integer',ST)
				TAC.emit(op='+',lhs=t5,op1=t4,op2=tp)
			t6 = TAC.newTemp('Integer',ST)
			TAC.emit(op='*',lhs=t6,op1=t5,op2=ST.getWidth(p[1]['type']))
			# Need to care about base address later on
			p[0]['tag'] = p[1]['tag'] + '+' + t6
	elif (p[1]['what'] == 'function' or p[1]['what'] == 'procedure'):
		if len(p[3]) != len(ST.getAttrVal(p[1]['tag'],'param_dict')):
			print('ERROR: Different number of arguments needed !')
			p_error(p)
		else:		
			param_s = ''
			for param in p[3]:
				param_s += str(param['tag'] if TAC.isDict(param) else param)	
			TAC.emit(op='call', lhs=p[1]['tag'], op1=param_s)
	else:
		p[0] = p[1]['tag']
		if p[1]['tag'] == 'print':
			if not isinstance(p[3],str):
				for item in p[3]:
					TAC.emit(op='print', op1=item)
			else:
				TAC.emit(op='print', op1=p[3])
		elif p[1]['tag'] == 'scan':
			if len(p[3]) > 1:
				print('ERROR: Only one variable can be scanned at a time !')
				p_error(p)
			for item in p[3]:
				TAC.emit(op='scan', op1=item)
		else:
			print("ERROR: Function not defined !")
			p_error(p)

def p_value_s(p):
	'''value_s : value
	   | value_s ',' value
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_value(p):
	'''value : simple_expression
	'''
	p[0] = deepcopy(p[1])

def p_literal(p):
	'''literal : numeric_lit
	'''
	p[0] = deepcopy(p[1])

def p_numeric_lit1 (p):
	'''numeric_lit : INT
	'''
	p[0] = {'tag' : p[1], 'type': 'Integer'}

def p_numeric_lit2 (p):
	'''numeric_lit : FLOAT
	'''
	p[0] = {'tag' : p[1], 'type': 'Float'}

def p_M (p):
	''' M : 
	'''
	p[0] = {'quad': TAC.getLine()}

def p_expression(p):
	'''expression : relation
	   | expression logical M relation
	'''
	if (len(p) == 2):
		p[0] = p[1]
	else:
		if (p[1]['type'] != 'bool' or p[4]['type'] != 'bool'):
			print('ERROR: One or more expression is not of boolean type !')
			p_error(p)
		else:	
			p[0] = deepcopy(p[4])
			temp_var = TAC.newTemp('bool', ST)
			p[0]['tag'] = temp_var
			if (p[2] == 'OR'):
				TAC.backpatch(p[1]['false_list'],p[3]['quad'])
				p[0]['true_list'] = TAC.merge(p[1]['true_list'],p[4]['true_list'])
				p[0]['false_list'] = p[4]['false_list']
			elif (p[2] == 'AND'):
				TAC.backpatch(p[1]['true_list'],p[3]['quad'])
				p[0]['true_list'] = p[4]['true_list']
				p[0]['false_list'] = TAC.merge(p[1]['false_list'], p[4]['false_list'])

def p_logical(p):
	'''logical : AND
	   | OR
	'''
	p[0] = p[1]

def p_relation(p):
	'''relation : simple_expression relational simple_expression
	'''
	if p[1]['type'] != p[3]['type']:
		print("ERROR: Comparison among different types !")
		p_error(p)
		p[0]={'type': None, 'true_list':[], 'false_list':[]}
	else:	
		p[0] = {}
		p[0]['type'] = 'bool'
		p[0]['true_list'] = TAC.makeList(TAC.getLine())
		p[0]['false_list'] = TAC.makeList(TAC.getLine() + 1)
		TAC.emit(op='goto_' + p[2], op1=p[1], op2=p[3])
		TAC.emit(op='goto')
	
def p_relational(p):
	'''relational : '='
	   | NEQ
	   | '<'
	   | LEQ
	   | '>'
	   | GEQ
	'''
	p[0] = p[1]
	
def p_simple_expression(p):
	'''simple_expression : term
	   | simple_expression adding term
	'''
	if (len(p) == 2):
		p[0] = deepcopy(p[1])
	else:
		op_type = ''
		if ((p[1]['type'] != 'Integer' and p[1]['type'] != 'Float') or (p[3]['type'] != 'Integer' and p[3]['type'] != 'Float')):
			print (p[1], p[3])
			print("ERROR: Expression terms are not numbers !")
			p_error(p)
		else:
			if (p[1]['type'] != p[3]['type']):
				op_type = 'float'
				temp_var = TAC.newTemp('Float', ST)
				x = {}
				if (p[1]['type'] == 'Integer'):
					TAC.emit(op='typecast', op1=p[1]['tag'], op2='Float', lhs=temp_var)
					p[1]['type'] = 'Float'
					p[1]['tag'] = temp_var
					p[0] = deepcopy(p[1])
				elif (p[3]['type'] == 'Integer'):
					TAC.emit(op='typecast', op1=p[3]['tag'], op2='Float', lhs=temp_var)
					p[3]['type'] = 'Float'
					p[3]['tag'] = temp_var
					p[0] = deepcopy(p[3])
			if (op_type != 'float'):
				p[0] = deepcopy(p[1])
			temp_var = TAC.newTemp('Integer', ST) if op_type == '' else TAC.newTemp('Float', ST) 
			op = p[2]+'_float' if op_type == 'float' else p[2]
			TAC.emit(op=op,lhs=temp_var,op1=p[1],op2=p[3])
			p[0]['tag'] = temp_var

def p_adding(p):
	'''adding  : '+'
	   | '-'
	'''
	p[0] = p[1]
	
def p_term(p):
	'''term : factor
	   | term multiplying factor
	'''
	if (len(p) == 2):
		p[0] = deepcopy(p[1])
	else:
		op_type = ''
		if ((p[1]['type'] != 'Integer' and p[1]['type'] != 'Float') or (p[3]['type'] != 'Integer' and p[3]['type'] != 'Float')):
			print (p[1], p[3])
			print('ERROR: Expression terms are not numbers !')
			p_error(p)
		elif (p[2] == 'mod' and p[1]['type'] != 'Integer'):
			print ('ERROR: Modulo supports integers only !')
			p_error(p)
		else:
			if (p[1]['type'] != p[3]['type']):
				op_type = 'float'
				temp_var = TAC.newTemp('Float', ST)
				x = {}
				if (p[1]['type'] == 'Integer'):
					TAC.emit(op='typecast', op1=p[1]['tag'], op2='Float', lhs=temp_var)
					p[1]['type'] = 'Float'
					p[1]['tag'] = temp_var
					p[0] = deepcopy(p[1])
				elif (p[3]['type'] == 'Integer'):
					TAC.emit(op='typecast', op1=p[3]['tag'], op2='Float', lhs=temp_var)
					p[3]['type'] = 'Float'
					p[3]['tag'] = temp_var
					p[0] = deepcopy(p[3])
			if (op_type != 'float'):
				p[0] = deepcopy(p[1])
			temp_var = TAC.newTemp('Integer', ST) if op_type == '' else TAC.newTemp('Float', ST) 
			op = p[2]+'_float' if op_type == 'float' else p[2]
			TAC.emit(op=op,lhs=temp_var,op1=p[1],op2=p[3])
			p[0]['tag'] = temp_var

def p_multiplying(p):
	'''multiplying : '*'
	   | '/'
	   | MOD
	   | STARSTAR
	'''
	p[0] = p[1]

# need to handle NOT
def p_factor(p):
	'''factor : primary
	'''
	p[0] = deepcopy(p[1])

def p_primary(p):
	'''primary : literal
	   | name
	   | parenthesized_primary
	'''
	p[0] = deepcopy(p[1])

def p_parenthesized_primary(p):
	'''parenthesized_primary : '(' simple_expression ')'
	'''
	p[0] = deepcopy(p[2])
	
def p_statement_s(p):
	'''statement_s : statement
	   | statement_s M statement
	'''
	p[0] = deepcopy(p[1])
	if (len(p) > 2):
		p[0] = deepcopy(p[1])
		TAC.backpatch(p[1]['next_list'], p[2]['quad'])
		p[0]['next_list'] = p[3]['next_list']
	
def p_statement(p):
	'''statement : simple_stmt
		| compound_stmt
	'''
	p[0] = deepcopy(p[1])
	p[0]['what'] = 'statement'

def p_simple_stmt(p):
	'''simple_stmt : assign_stmt
	   | return_stmt
	   | procedure_call
	'''
	p[0] = deepcopy(p[1])

def p_compound_stmt(p):
	'''compound_stmt : if_stmt
	   | loop_stmt
	'''
	p[0] = deepcopy(p[1])

def p_lambda_decl (p):
	'''lambda_decl : lambda_begin simple_expression ';'
	'''
	global ST
	ST = ST.endScope();
	p[0] = deepcopy(p[1])
	p[0]['next_list'] = []

def p_lambda_begin (p):
	'''lambda_begin : def_id ASSIGN LAMBDA param ':'
	'''
	global ST
	f_name = p[1]
	attr_dict = {'tag': f_name, 'what': 'lambda_function', 'param_dict': p[4]}
	ST.insert(f_name, attr_dict)
	ST = ST.beginScope()
	for k,v in attr_dict['param_dict'].items():
		ST.insert(k, v)
	p[0] = ST.parentTable.table[f_name]

def p_assign_stmt(p):
	'''assign_stmt : name ASSIGN simple_expression ';'
	'''
	p[0] = {}
	p[0]['type'] = 'assign_stmt'
	p[0]['next_list'] = []
	if p[1] == None :
		p_error(p)
	else:
		if (p[1]['type'] == 'Integer' and p[3]['type'] == 'Float'):
			print('ERROR: Variables not of same type !')
			p_error(p)
		else:		
			TAC.emit(lhs=p[1]['tag'],op1=p[3],op='=')
	
def p_if_stmt(p):
	'''if_stmt : IF cond_clause else_opt END IF ';'
	'''
	p[0] = {}
	p[0]['type'] = 'if_stmt'
	p[0]['next_list'] = TAC.merge(p[2]['next_list'], p[3]['next_list'])
	TAC.backpatch(p[2]['false_list'], p[3]['quad'])

def p_N (p):
	'''N :
	'''
	p[0] = {'quad': TAC.getLine()}
	TAC.emit(op='goto')

# Changed the last statement, it was buggy # p[0]['next_list'] = merge([p[2]["quad"]], p[4]["nextlist"])
def p_cond_clause(p):
	'''cond_clause : condition THEN M statement_s N
	'''
	p[0] = deepcopy(p[1])
	p[0]['next_list'] = [p[5]['quad']]
	TAC.backpatch(p[1]['true_list'], p[3]['quad'])
	
def p_condition(p):
	'''condition : expression
	'''
	if(p[1]['type']!='bool'):
		print('ERROR: Condition not boolean !')
		p_error(p)
		p[0] = {'false_list':[],'true_list':[],'tag':None , 'type':None}
	else:	
		p[0] = deepcopy(p[1])
	
	
def p_else_opt(p):
	'''else_opt :
	   | ELSE M statement_s
	'''
	if len(p) == 1:
		p[0] = {'next_list': []}
		p[0]['quad'] = TAC.getLine()
	else:
		p[0] = deepcopy(p[3])
		p[0]['quad'] = p[2]['quad']
	
def p_loop_stmt(p):
	'''loop_stmt : iteration M basic_loop ';'
	'''
	p[0] = deepcopy(p[3])
	TAC.backpatch(p[3]['next_list'], p[1]['quad'])
	TAC.emit(op='goto', lhs=p[1]['quad'])
	TAC.backpatch(p[1]['true_list'], p[2]['quad'])
	p[0]['next_list'] = p[1]['false_list']

def p_iteration(p):
	'''iteration : WHILE M condition
		| FOR IDENTIFIER IN range
	'''
	if (len(p) == 4):
		p[0] = deepcopy(p[3])
		p[0]['quad'] = p[2]['quad']
	else: 
		p[0] = {}
		TAC.emit(op='=',lhs=p[2],op1=p[4]['r_start'])
		TAC.emit(op='goto',lhs=TAC.getLine()+2)
		p[0]['quad'] = TAC.getLine()
		TAC.emit(op='+', lhs=p[2], op1=p[2] , op2=1)
		p[0]['true_list'] = TAC.makeList(TAC.getLine())
		p[0]['false_list'] = TAC.makeList(TAC.getLine() + 1)
		TAC.emit(op='goto_<=', op1=p[2], op2=p[4]['r_end'])
		TAC.emit(op='goto')

	
def p_basic_loop(p):
	'''basic_loop : LOOP statement_s END LOOP
	'''
	p[0] = deepcopy(p[2])
	
def p_block_body(p):
	'''block_body : BEGIN statement_s
	'''
	p[0] = deepcopy(p[2])

def p_return_stmt(p):
	'''return_stmt : RETURN ';'
	   | RETURN simple_expression ';'
	'''
	p[0] = {}
	p[0]['type'] = 'return_stmt'
	p[0]['return_what'] = p[2] if len(p) > 2 else {}
	p[0]['next_list'] = []
	TAC.emit (op='return',op1=p[2])

def p_subprog_decl(p):
	'''subprog_decl : subprog_spec ';'
	'''
	p[0] = deepcopy(p[1])

def p_subprog_spec(p):
	'''subprog_spec : PROCEDURE def_id formal_part_opt
	   | FUNCTION def_id formal_part_opt RETURN name
	'''
	sp_name = p[2]
	if (len(p) == 4):
		if (p[2] in reserved):
			print('ERROR: Procedure name is reserved keyword !')
			p_error(p)
		elif (ST.doesExist(p[2])):
			print('ERROR: Procedure name already used !')
			p_error(p)
		else:		
			attr_dict = {'tag': sp_name, 'param_dict': p[3], 'what': 'procedure'}
	else:
		attr_dict = {'tag': sp_name, 'param_dict': p[3], 'what': 'function', 'type': p[5]}
	ST.insert(sp_name, attr_dict)
	p[0] = ST.getAttrDict(sp_name)
	
def p_formal_part_opt(p):
	'''formal_part_opt : 
	   | formal_part
	'''
	p[0] = {} if len(p) == 1 else p[1]
	
def p_formal_part(p):
	'''formal_part : '(' param_s ')'
	'''
	p[0] = deepcopy(p[2])

def p_param_s(p):
	'''param_s : param
	   | param_s ';' param
	'''
	if (len(p) == 2):
		p[0] = deepcopy(p[1])
	else:
		p[0] = {**p[1], **p[3]}

def p_param(p):
	'''param : def_id_s ':' mark
	'''
	if(p[3] == None):
		print('ERROR: Parameter type missing !')
		p_error(p)
	else:	
		def_id_s = p[1]
		p[0] = {}
		for id in def_id_s:
			dtype = p[3]['tag']
			attr_dict = {'tag': id, 'what': 'var', 'type': dtype}
			p[0][id] = attr_dict

def p_subprog_spec_is_push(p):
	'''subprog_spec_is_push : subprog_spec IS
	'''
	global ST
	p[0] = deepcopy (p[1])
	p[0]['next_list'] = [] if ST.parentTable == None else [TAC.getLine()]
	ST = ST.beginScope()
	for param, param_attr_dict in p[1]['param_dict'].items():
		ST.insert(param, param_attr_dict)

def p_subprog_body(p):
	'''subprog_body : subprog_spec_is_push decl_part block_body END ';'
	'''
	global ST
	p[0] = deepcopy(p[3])
	ST.printTable();
	ST = ST.endScope()
	
def p_procedure_call(p):
	'''procedure_call : name ';'
	'''
	p[0] = {}
	p[0]['type'] = 'procedure_call'
	p[0]['call_what'] = p[1]['tag']
	p[0]['next_list'] = []
	TAC.emit(op='call', lhs=p[1]['tag'])
	
def p_use_clause(p):
	'''use_clause : USE name_s ';'
	'''
	p[0] = deepcopy(p[2])
	
def p_name_s(p):
	'''name_s : name
	   | name_s ',' name
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]
	
def p_compilation(p):
	'''compilation :
	   | compilation comp_unit
	   | pragma pragma_s
	'''
	
def p_comp_unit(p):
	'''comp_unit : context_spec unit pragma_s
	   | unit pragma_s
	'''
	
def p_context_spec(p):
	'''context_spec : with_clause use_clause_opt
	   | context_spec with_clause use_clause_opt
	   | context_spec pragma
	'''
	
def p_with_clause(p):
	'''with_clause : WITH c_name_list ';'
	'''
	
def p_use_clause_opt(p):
	'''use_clause_opt :
	   | use_clause_opt use_clause
	'''
	
def p_unit(p):
	'''unit : subprog_decl
	   | subprog_body
	'''
	p[0] = p[1]

def p_error(p):
	global err
	err = True
	print("Error in input program!", str(p.lineno),'\n')