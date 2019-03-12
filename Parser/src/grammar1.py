# http://www.adaic.org/resources/add_content/standards/95lrm/grammar9x.y

import sys, re, os, logging
from ply import lex, yacc

from Tokens import *

from symtab import SymbolTable


root = None

def appropriate (L):
	A = []
	for item in L:
		if isinstance(item,Node):
			A.append(item)
	return (A)

class Node:
	def __init__(self, typ, children=None, desig=''):
		self.visited = False
		self.typ = typ
		self.desig = desig
		self.children = appropriate(children) if children else []

def p_goal_symbol(p):
	'''goal_symbol : compilation
	'''
	global root
	p[0] = Node('goal_symbol',[p[1]], 'START')
	root = p[0]

def p_pragma(p):
	'''pragma : PRAGMA IDENTIFIER ';'
	   | PRAGMA simple_name '(' pragma_arg_s ')' ';'
	'''
	if (len(p) == 4):
		p[0] = Node('pragma', None, p[1])
	else:
		p[0] = Node ('pragma', [p[2],p[4]], p[1])

def p_pragma_arg_s(p):
	'''pragma_arg_s : pragma_arg
	   | pragma_arg_s ',' pragma_arg
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'pragma_arg_s'
	else:
		p[0] = Node('pragma_arg_s', [p[1],p[3]])

def p_pragma_arg(p):
	'''pragma_arg : expression
	   | simple_name ARROW expression
	'''	
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'pragma_arg'
	else:
		p[0] = Node('pragma_arg', [p[1],p[3]], p[2])

def p_pragma_s(p):
	'''pragma_s :
	   | pragma_s pragma
	'''
	if (len(p) > 1):
		p[0] = Node('pragma_s', [p[1],p[2]])
	else:
		p[0] = Node ('pragma_s', None)

def p_decl(p):
	'''decl : object_decl
	   | type_decl
	   | subtype_decl
	   | subprog_decl
	   | error ';'
	'''
	p[0] = p[1]
	p[0].typ = 'decl'

def p_object_decl(p):
	'''object_decl : def_id_s ':' object_subtype_def init_opt ';'   
	'''
	var_list = p[1].desig.split(',')
	var_type = p[3].desig
	print ('Declaration', var_list, var_type)
	p[0] = Node('object_decl', [p[1],p[3],p[4],p[5]], p[2])

def p_def_id_s(p):
	'''def_id_s : def_id
	   | def_id_s ',' def_id
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'def_id_s'
	else:
		s = str(p[1].desig) + ',' + str(p[3].desig)
		p[0] = Node('def_id_s', None, s)

def p_def_id(p):
	'''def_id  : IDENTIFIER
	'''
	p[0] = Node('def_id', None, p[1])

def p_object_subtype_def(p):
	'''object_subtype_def : subtype_ind
	   | array_type
	'''
	p[0] = p[1]
	p[0].typ = 'object_subtype_def'

def p_init_opt(p):
	'''init_opt :
	   | ASSIGN expression
	'''
	if (len(p) > 1):
		p[0] = Node('init_opt', [p[2]], p[1])
	else:
		p[0] = Node ('init_opt', None)

def p_type_decl(p):
	'''type_decl : TYPE IDENTIFIER discrim_part_opt type_completion ';'
	'''
	s = p[1] + ' ' + p[2]
	p[0] = Node ('type_decl', [p[3],p[4]], s)

def p_discrim_part_opt(p):
	'''discrim_part_opt :
	   | discrim_part
	   | '(' BOX ')'
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'discrim_part_opt'
	elif (len(p) == 4):
		p[0] = Node('discrim_part_opt', None, p[2])
	else:
		p[0] = Node ('discrim_part_opt', None)
	
def p_type_completion(p):
	'''type_completion :
	   | IS type_def
	'''
	if (len(p) > 1):
		p[0] = Node ('type_completion', [p[2]], p[1])
	else:
		p[0] = Node ('type_completion', None)

def p_type_def(p):
	'''type_def : integer_type
	   | array_type
	   | record_type
	'''
	p[0] = p[1]
	p[0].typ = 'type_def'
	
def p_subtype_decl(p):
	'''subtype_decl : SUBTYPE IDENTIFIER IS subtype_ind ';'
	'''
	s = p[1] + ' ' + p[2]
	p[0] = Node ('subtype_decl', [p[4]], s)

def p_subtype_ind(p):
	'''subtype_ind : name constraint
	   | name
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'subtype_ind'
	else:
		p[0] = Node ('subtype_ind', [p[2]] ,p[1].desig)
	
def p_constraint(p):
	'''constraint : range_constraint
	'''
	p[0] = p[1]
	p[0].typ = 'constraint'
	
def p_range_constraint(p):
	'''range_constraint : RANGE range
	'''
	p[0] = p[2]
	p[0].typ = 'range_constraint'

def p_range(p):
	'''range : simple_expression DOTDOT simple_expression
	'''
	p[0] = Node ('range', [p[1],p[3]], desig='..')
		
def p_integer_type(p):
	'''integer_type : range_spec
	   | MOD expression
	'''
	if (len(p) == 2):
		p[0] = Node ('integer_type', None, p[1])
	else:
		p[0] = Node ('integer_type', [p[2]], p[1])
	
def p_range_spec(p):
	'''range_spec : range_constraint
	'''
	p[0] = p[1]
	p[0].typ = 'range_spec'

def p_array_type(p):
	'''array_type : constr_array_type
	'''
	p[0] = p[1]
	p[0].typ = 'array_type'
	
def p_constr_array_type(p):
	'''constr_array_type : ARRAY iter_index_constraint OF component_subtype_def
	'''
	p[0] = Node ('constr_array_type', [p[2],p[4]], p[1])
	
def p_component_subtype_def(p):
	'''component_subtype_def : subtype_ind
	'''
	p[0] = p[1]
	p[0].typ = 'component_subtype_def'
	
def p_iter_index_constraint(p):
	'''iter_index_constraint : '(' iter_discrete_range_s ')'
	'''
	p[0] = p[2]
	p[0].typ = 'iter_index_constraint'
	
def p_iter_discrete_range_s(p):
	'''iter_discrete_range_s : discrete_range
	   | iter_discrete_range_s ',' discrete_range
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'iter_discrete_range_s'
	else:
		p[0] = Node ('iter_discrete_range_s', [p[1], p[3]], p[0])
	
def p_discrete_range(p):
	'''discrete_range : name range_constr_opt
	   | range
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'discrete_range'
	else:
		p[0] = Node ('p_discrete_range', [p[1],p[2]], p[0])
	
def p_range_constr_opt(p):
	'''range_constr_opt :
	   | range_constraint
	'''
	if (len(p) > 1):
		p[0] = p[1]
		p[0].typ = 'range_constr_opt'
	else:
		p[0] = Node ('array_type', None, p[0])
	
def p_record_type(p):
	'''record_type : record_def
	'''
	p[0] = Node ('record_type', [p[1],p[2]], p[0])
	
def p_record_def(p):
	'''record_def : RECORD pragma_s comp_list END RECORD
	   | NuLL RECORD
	'''
	if (len(p) == 3):
		s = p[1] + ' ' + p[2]
		p[0] = Node ('record_def', None, p[0], s)
	else:
		p[0] = Node ('record_def', [p[2],p[3]], p[0], desig = p[1])

def p_comp_list(p):
	'''comp_list : NuLL ';' pragma_s
	'''
	p[0] = Node ('comp_list', [p[1],p[3]], p[0])
	
def p_discrim_part(p):
	'''discrim_part : '(' discrim_spec_s ')'
	'''
	p[0] = Node ('discrim_part', None, p[2])
	
def p_discrim_spec_s(p):
	'''discrim_spec_s : discrim_spec
	   | discrim_spec_s ';' discrim_spec
	'''
	p[0] = Node('discrim_spec_s', None, p[0])

def p_discrim_spec(p):
	'''discrim_spec : def_id_s ':' mark init_opt
	   | error
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'discrim_spec'
	else:
		p[0] = Node ('discrim_spec', [p[1],p[3],p[4]], p[2])
	
	
def p_discrete_with_range(p):
	'''discrete_with_range : name range_constraint
	   | range
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'discrete_with_range'
	else:
		p[0] = Node ('discrete_with_range', [p[1],p[2]])

def p_decl_part(p):
	'''decl_part :
	   | decl_item_or_body_s
	'''
	if (len(p) > 1):
		p[0] = p[1]
		p[0].typ = 'decl_part'
	else:
		p[0] = Node ('decl_part', None)

def p_decl_item(p):
	'''decl_item : decl
	   | use_clause
	   | pragma
	'''
	p[0] = p[1]
	p[0].typ = 'decl_item'

def p_decl_item_or_body_s(p):
	'''decl_item_or_body_s : decl_item_or_body
	   | decl_item_or_body_s decl_item_or_body
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'decl_item_or_body_s'
	else:
		p[0] = Node ('decl_item_or_body_s', [p[1],p[2]])
	
def p_decl_item_or_body(p):
	'''decl_item_or_body : body
	   | decl_item
	'''
	p[0] = p[1]
	p[0].typ = 'decl_item_or_body'
	
def p_body(p):
	'''body : subprog_body
	'''
	p[0] = p[1]
	p[0].typ = 'body'

def p_name(p):
	'''name : simple_name
	   | indexed_comp
	   | selected_comp
	   | attribute
	   | operator_symbol
	'''
	p[0] = p[1]
	p[0].typ = 'name'
	
def p_mark(p):
	'''mark : simple_name
	   | mark TICK attribute_id
	   | mark '.' simple_name
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'mark'
	else:
		p[0] = Node ('mark', [p[1],p[3]], p[2])

def p_simple_name(p):
	'''simple_name : IDENTIFIER
	'''
	p[0] = Node('simple_name', None, p[1])
	
def p_compound_name(p):
	'''compound_name : simple_name
	   | compound_name '.' simple_name
	'''
	if (len(p) == 2):
		p[0] = Node ('compound_name', None, p[1].desig)
	else:
		s = p[1].desig + '.' + p[3].desig
		p[0] = Node ('compound_name', None, s)	
	
def p_c_name_list(p):
	'''c_name_list : compound_name
	    | c_name_list ',' compound_name
	'''
	if (len(p) == 2):
		p[0] = Node ('c_name_list', None, p[1].desig)
	else:
		s = p[1].desig + ', ' + p[3].desig
		p[0] = Node ('c_name_list', None, s)
	
def p_used_char(p):
	'''used_char : CHAR
	'''
	p[0] = Node('used_char', None, p[1])
	
def p_operator_symbol(p):
	'''operator_symbol : STRING
	'''
	p[0] = Node('operator_symbol', None, p[1])
	
def p_indexed_comp(p):
	'''indexed_comp : name '(' value_s ')'
	'''
	s = str(p[1].desig) + '(' + str(p[3].desig) + ')'
	p[0] = Node ('indexed_comp', [p[1],p[3]], s)
	
def p_value_s(p):
	'''value_s : value
	   | value_s ',' value
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'value_s'
	else:
		s = str(p[1].desig) + ',' + str(p[3].desig)
		p[0] = Node ('value_s', [p[1],p[3]], s)

def p_value(p):
	'''value : expression
	   | discrete_with_range
	   | error
	'''
	p[0] = p[1]
	p[1].typ = 'value'
	
def p_selected_comp(p):
	'''selected_comp : name '.' simple_name
	   | name '.' used_char
	   | name '.' operator_symbol
	   | name '.' ALL
	'''
	s = p[1].desig + '.' + p[3].desig
	p[0] = Node('selected_comp', None, s)
	
def p_attribute(p):
	'''attribute : name TICK attribute_id
	'''
	p[0] = Node ('attribute', [p[1],p[3]], p[2])
	
def p_attribute_id(p):
	'''attribute_id : IDENTIFIER
	   | DIGITS
	'''
	p[0] = Node('attribute_id', None, p[1])
	
def p_literal(p):
	'''literal : INT
	   | NuLL
	'''
	p[0] = Node('literal', None, p[1])
	
	
def p_expression(p):
	'''expression : relation
	   | expression logical relation
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'expression'
	else:
		p[0] = Node ('expression', [p[1],p[3]], p[2])
	
def p_logical(p):
	'''logical : AND
	   | OR
	   | XOR
	'''
	p[0] = Node('logical', None, p[1])
	
def p_relation(p):
	'''relation : simple_expression
	   | simple_expression relational simple_expression
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'relation'
	else:
		p[0] = Node ('relation', [p[1],p[3]], p[2].desig)
	
def p_relational(p):
	'''relational : '='
	   | NEQ
	   | '<'
	   | LEQ
	   | '>'
	   | GEQ
	'''
	p[0] = Node('relational', None, p[1])
	
def p_simple_expression(p):
	'''simple_expression : term
	   | simple_expression adding term
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'simple_expression'
	else:
		p[0] = Node ('simple_expression', [p[1],p[3]], p[2].desig)

def p_adding(p):
	'''adding  : '+'
	   | '-'
	   | '&'
	'''
	p[0] = Node('adding', None, p[1])
	
def p_term(p):
	'''term    : factor
	   | term multiplying factor
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'term'
	else:
		p[0] = Node ('term', [p[1],p[3]], p[2].desig)
	
def p_multiplying(p):
	'''multiplying : '*'
	   | '/'
	   | MOD
	   | REM
	   | STARSTAR
	'''
	p[0] = Node('multiplying', None, p[1])
	
def p_factor(p):
	'''factor : primary
	'''
	p[0] = p[1]
	p[0].typ = 'factor'

def p_primary(p):
	'''primary : literal
	   | name
	   | parenthesized_primary
	'''
	p[0] = p[1]
	p[0].typ = 'primary'
	
def p_parenthesized_primary(p):
	'''parenthesized_primary : '(' expression ')'
	'''
	p[0] = p[2]
	p[0].typ = 'parenthesized_primary'

	
def p_statement_s(p):
	'''statement_s : statement
	   | statement_s statement
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'statement_s'
	else:
		p[0] = Node ('statement_s', [p[1],p[2]])
	
def p_statement(p):
	'''statement : unlabeled
	   | label statement
	'''
	if (len(p) == 2):
		p[0] = p[1]
	else:
		p[0] = Node ('statement', [p[1]]+p[2].children, p[0])
	
def p_unlabeled(p):
	'''unlabeled : simple_stmt
	   | compound_stmt
	'''
	p[0] = p[1]
	p[0].typ = 'unlabeled'

def p_simple_stmt(p):
	'''simple_stmt : null_stmt
	   | assign_stmt
	   | return_stmt
	   | procedure_call
	   | error ';'
	'''
	p[0] = p[1]
	p[0].typ = 'simple_stmt'

def p_compound_stmt(p):
	'''compound_stmt : if_stmt
	   | loop_stmt
	   | block
	'''
	p[0] = p[1]
	p[0].typ = 'compound_stmt'

def p_label(p):
	'''label : LL IDENTIFIER RR
	'''
	s = p[1] + ' ' + p[2] + ' ' + p[3]
	p[0] = Node('label', None, s)
	
def p_null_stmt(p):
	'''null_stmt : NuLL ';'
	'''
	p[0] = Node('null_stmt', None, p[1])
	
def p_assign_stmt(p):
	'''assign_stmt : name ASSIGN expression ';'
	'''
	var = p[1].desig
	p[0] = Node ('assign_stmt', [p[1],p[3]], p[2])
	
def p_if_stmt(p):
	'''if_stmt : IF cond_clause_s else_opt END IF ';'
	'''
	p[0] = Node ('if_stmt', [p[2],p[3]], p[1])
	
def p_cond_clause_s(p):
	'''cond_clause_s : cond_clause
	   | cond_clause_s ELSIF cond_clause
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'cond_clause_s'
		p[0].desig = 'no_elsif'
	else:
		p[0] = Node ('cond_clause_s', [p[1],p[3]], p[2])

def p_cond_clause(p):
	'''cond_clause : cond_part statement_s
	'''
	p[0] = Node ('cond_clause', [p[1],p[2]])
	
def p_cond_part(p):
	'''cond_part : condition THEN
	'''
	p[0] = Node ('cond_part', [p[1]], p[2])
	
def p_condition(p):
	'''condition : expression
	'''
	p[0] = p[1]
	p[0].typ = 'condition'
	
def p_else_opt(p):
	'''else_opt :
	   | ELSE statement_s
	'''
	if (len(p) > 1):
		p[0] = Node ('else_opt', [p[2]], p[1])
	else:
		p[0] = Node ('else_opt', None)
	
def p_loop_stmt(p):
	'''loop_stmt : label_opt iteration basic_loop id_opt ';'
	'''
	p[0] = Node ('loop_stmt', [p[1],p[2],p[3],p[4]], desig='LOOP_STMT')
	
def p_label_opt(p):
	'''label_opt :
	   | IDENTIFIER ':'
	'''
	if (len(p) > 1):
		p[0] = Node ('label_opt', None, p[1])

def p_iteration(p):
	'''iteration :
	   | WHILE condition
	'''
	if (len(p) > 1):
		p[0] = Node ('iteration', [p[2]], p[1])
	
def p_basic_loop(p):
	'''basic_loop : LOOP statement_s END LOOP
	'''
	p[0] = Node ('basic_loop', [p[2]], p[1])
	
def p_id_opt(p):
	'''id_opt :
	   | designator
	'''
	if (len(p) > 1):
		p[0] = Node ('id_opt', None, p[1].desig)
	else:
		p[0] = Node ('id_opt', None)

def p_block(p):
	'''block : label_opt block_decl block_body END id_opt ';'
	'''
	p[0] = Node ('block', [p[1],p[2],p[3]], 'BLOCK')
	
def p_block_decl(p):
	'''block_decl :
	   | DECLARE decl_part
	'''
	if (len(p) > 1):
		p[0] = Node ('block_decl', [p[2]], p[1])
	else:
		p[0] = Node ('block_decl', None)
	
def p_block_body(p):
	'''block_body : BEGIN statement_s
	'''
	p[0] = Node ('block_body', [p[2]], p[1])
	
def p_return_stmt(p):
	'''return_stmt : RETURN ';'
	   | RETURN expression ';'
	'''
	if (len(p) == 2):
		p[0] = Node ('return_stmt', None, p[1])
	else:
		p[0] = Node ('return_stmt', [p[2]], p[1])

def p_subprog_decl(p):
	'''subprog_decl : subprog_spec ';'
	'''
	p[0] = p[1]
	p[0].typ = 'subprog_decl'
	
def p_subprog_spec(p):
	'''subprog_spec : PROCEDURE compound_name formal_part_opt
	   | FUNCTION designator formal_part_opt RETURN name
	   | FUNCTION designator
	'''
	if (len(p) == 3):
		p[0] = Node ('subprog_spec', [p[2]], p[1])
	elif (len(p) == 6):
		p[0] = Node ('subprog_spec', [p[2],p[3],p[5]], p[1])
	else:
		p[0] = Node ('subprog_spec', [p[2],p[3]], p[1])
	
def p_designator(p):
	'''designator : compound_name
	   | STRING
	'''
	if (isinstance(p[1],str)):
		p[0] = Node('designator', None, p[1])
	else:
		p[0] = p[1]
		p[0].typ = 'designator'
	
	
def p_formal_part_opt(p):
	'''formal_part_opt : 
	   | formal_part
	'''
	if (len(p) > 1):
		p[0] = p[1]
		p[0].typ = 'formal_part_opt'
	else:
		p[0] = Node ('formal_part_opt', None)
	
def p_formal_part(p):
	'''formal_part : '(' param_s ')'
	'''
	p[0] = p[2]
	p[0].typ = 'formal_part'
	
def p_param_s(p):
	'''param_s : param
	   | param_s ';' param
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'param_s'
	else:
		p[0] = Node ('param_s', [p[1], p[3]], p[0])
	
def p_param(p):
	'''param : def_id_s ':' mark init_opt
	   | error
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'param'
	else:
		p[0] = Node ('param', [p[1],p[3],p[4]], p[0])
	
def p_subprog_spec_is_push(p):
	'''subprog_spec_is_push : subprog_spec IS
	'''
	p[0] = Node ('subprog_spec_is_push', [p[1]], 'IS')
	
def p_subprog_body(p):
	'''subprog_body : subprog_spec_is_push decl_part block_body END id_opt ';'
	'''
	p[0] = Node ('subprog_body', [p[1],p[2],p[3],p[5]])
	
def p_procedure_call(p):
	'''procedure_call : name ';'
	'''
	p[0] = p[1]
	p[0].typ = 'procedure_call'
	
def p_use_clause(p):
	'''use_clause : USE name_s ';'
	   | USE TYPE name_s ';'
	'''
	if (len(p) == 4):
		p[0] = Node('use_clause', [p[2]], 'USE')
	else:
		p[0] = Node('use_clause', [p[3]], 'USE TYPE')
	
def p_name_s(p):
	'''name_s : name
	   | name_s ',' name
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'name_s'
	else:
		s = p[1].desig + ', ' + p[3].desig
		p[0] = Node ('name_s', [p[1],p[3]], s)
	
def p_compilation(p):
	'''compilation :
	   | compilation comp_unit
	   | pragma pragma_s
	'''
	if (len(p) > 1):
		if (p[1].typ == 'compilation'):
			p[0] = Node('compilation', [p[1],p[2]])
		else:
			p[0] = Node ('compilation', [p[1],p[2]])
	else:
		p[0] = Node ('compilation', None)
	
def p_comp_unit(p):
	'''comp_unit : context_spec unit pragma_s
	   | unit pragma_s
	'''
	if (len(p) == 4):
		p[0] = Node('comp_unit', [p[1],p[2],p[3]])
	else:
		p[0] = Node('comp_unit', [p[1],p[2]])
	
def p_context_spec(p):
	'''context_spec : with_clause use_clause_opt
	   | context_spec with_clause use_clause_opt
	   | context_spec pragma
	''' 
	if (len(p) == 3):
		p[0] = Node('context_spec', [p[1],p[2]])
	else:
		p[0] = Node('context_spec', [p[1],p[2],p[3]])
	
def p_with_clause(p):
	'''with_clause : WITH c_name_list ';'
	'''
	p[0] = Node('with_clause',[p[2]], p[1])
	
def p_use_clause_opt(p):
	'''use_clause_opt :
	   | use_clause_opt use_clause
	'''
	if (len(p) > 1):
		p[0] = Node('use_clause_opt', [p[1],p[2]])
	else:
		p[0] = Node ('use_clause_opt', None)
	
def p_unit(p):
	'''unit : subprog_decl
	   | subprog_body
	'''
	p[0] = p[1]
	p[0].typ = 'unit'

def p_error(p):
	print ('line :',p.lineno,'-parse issue at token:',p.type)
	parser.errok()