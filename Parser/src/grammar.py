# http://www.adaic.org/resources/add_content/standards/95lrm/grammar9x.y

import sys, re, os, logging
from ply import lex, yacc

from Tokens import *

root = 1

def appropriate (L):
	A = []
	for item in L:
		if isinstance(item,Node):
			A.append(item)
	return (A)

class Node:
	def __init__(self,typ,children=None,leaf=None,desig=''):
		self.visited = False
		self.typ = typ
		self.desig = desig
		if children:
			self.children = appropriate(children)
		else:
			self.children = []
		self.leaf = leaf
	def getChildren (self):
		return (self.children + [self])

def p_goal_symbol(p):
	'''goal_symbol : compilation
    '''
	p[0] = Node('goal_symbol',[p[1]], p[0], 'START')
	global root
	root = p[0]

def p_pragma(p):
	'''pragma  : PRAGMA IDENTIFIER ';'
	   | PRAGMA simple_name '(' pragma_arg_s ')' ';'
	'''
	if (len(p) == 4):
		s = p[1] + ' ' + p[2]
		p[0] = Node('pragma', None, None, desig=s)
	else:
		p[0] = Node ('pragma', [p[2],p[4]], desig=p[1])

def p_pragma_arg_s(p):
	'''pragma_arg_s : pragma_arg
	   | pragma_arg_s ',' pragma_arg
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'pragma_arg_s'
	else:
		p[0] = Node('pragma_arg', [p[1],p[3]], p[0])

def p_pragma_arg(p):
	'''pragma_arg : expression
	   | simple_name ARROW expression
	'''	
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'pragma_arg'
	else:
		p[0] = Node('pragma_arg', [p[1],p[3]], p[0], desig=p[2])

def p_pragma_s(p):
	'''pragma_s :
	   | pragma_s pragma
	'''
	if (len(p) > 1):
		p[0] = Node('pragma_s', [p[1],p[2]], p[0])
	else:
		p[0] = Node ('pragma_s', None, p[0])

def p_decl(p):
	'''decl    : object_decl
	   | number_decl
	   | type_decl
	   | subtype_decl
	   | subprog_decl
	   | pkg_decl
	   | task_decl
	   | prot_decl
	   | exception_decl
	   | rename_decl
	   | generic_decl
	   | body_stub
	   | error ';'
	'''
	p[0] = p[1]
	p[0].typ = 'decl'

def p_object_decl(p):
	'''object_decl : def_id_s ':' object_qualifier_opt object_subtype_def init_opt ';'   
	'''
	p[0] = Node('object_decl',[p[1],p[3],p[4],p[5]] ,p[0], desig=p[2])


def p_def_id_s(p):
	'''def_id_s : def_id
	   | def_id_s ',' def_id
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'def_id_s'
	else:
		s = str(p[1].desig) + ',' + str(p[3].desig)
		p[0] = Node('def_id_s', [p[1],p[3]], p[0], desig = s)

def p_def_id(p):
	'''def_id  : IDENTIFIER
	'''
	p[0] = Node('def_id', None, None, desig=p[1])

def p_object_qualifier_opt(p):
	'''object_qualifier_opt :
	   | ALIASED
	   | CONSTANT
	   | ALIASED CONSTANT
	'''
	if (len(p) > 1):
		p[0] = Node('object_qualifier_opt', None, None, desig=p[1])
	else:
		p[0] = Node ('object_qualifier_opt', None, p[0])

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
		p[0] = Node('init_opt', None, p[2])
	else:
		p[0] = Node ('init_opt', None, p[0])

def p_number_decl(p):
	'''number_decl : def_id_s ':' CONSTANT ASSIGN expression ';'
	'''
	p[0] = Node ('number_decl', [p[1],p[5]], p[4])

def p_type_decl(p):
	'''type_decl : TYPE IDENTIFIER discrim_part_opt type_completion ';'
	'''
	s = p[1] + ' ' + p[2]
	p[0] = Node ('type_decl', [p[3],p[4]], p[0], desig=s)

def p_discrim_part_opt(p):
	'''discrim_part_opt :
	   | discrim_part
	   | '(' BOX ')'
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'discrim_part_opt'
	elif (len(p) == 4):
		p[0] = Node('discrim_part_opt', None, None, desig=p[2])
	else:
		p[0] = Node ('discrim_part_opt', None, p[0])
	
def p_type_completion(p):
	'''type_completion :
	   | IS type_def
	'''
	if (len(p) > 1):
		p[0] = Node ('type_completion', [p[2]], p[0], desig=p[1])
	else:
		p[0] = Node ('type_completion', None, p[0])

def p_type_def(p):
	'''type_def : enumeration_type 
	   | integer_type
	   | real_type
	   | array_type
	   | record_type
	   | access_type
	   | derived_type
	   | private_type
	'''
	p[0] = p[1]
	p[0].typ = 'type_def'
	
def p_subtype_decl(p):
	'''subtype_decl : SUBTYPE IDENTIFIER IS subtype_ind ';'
	'''
	p[0] = Node ('subtype_decl', [p[1],p[2],p[4]], p[3])

def p_subtype_ind(p):
	'''subtype_ind : name constraint
	   | name
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'subtype_ind'
	else:
		p[0] = Node ('subtype_ind', [p[1],p[2]] ,p[0])
	
def p_constraint(p):
	'''constraint : range_constraint
	   | decimal_digits_constraint
	'''
	p[0] = p[1]
	p[0].typ = 'constraint'

	
def p_decimal_digits_constraint(p):
	'''decimal_digits_constraint : DIGITS expression range_constr_opt
	'''
	p[0] = Node ('decimal_digits_constraint', [p[1],p[2],p[3]], p[0])
	
def p_derived_type(p):
	'''derived_type : NEW subtype_ind
	   | NEW subtype_ind WITH PRIVATE
	   | NEW subtype_ind WITH record_def
	   | ABSTRACT NEW subtype_ind WITH PRIVATE
	   | ABSTRACT NEW subtype_ind WITH record_def
	'''
	if (len(p) == 3):
		p[0] = Node ('derived_type', [p[2]], p[1])
	elif (len(p) == 5):
		p[0] = Node ('derived_type', [p[2],p[4]], p[1])
	else:
		p[o] = Node ('derived_type', [p[1],p[3],p[5]], p[2])
	
def p_range_constraint(p):
	'''range_constraint : RANGE range
	'''
	p[0] = p[2]
	p[0].typ = 'range_constraint'

def p_range(p):
	'''range : simple_expression DOTDOT simple_expression
	'''
	p[0] = Node ('range', [p[1],p[3]], p[0], desig='..')
	
def p_enumeration_type(p):
	'''enumeration_type : '(' enum_id_s ')'
	'''
	p[0] = Node ('enumeration_type', None, p[2])
	
def p_enum_id_s(p):
	'''enum_id_s : enum_id
	   | enum_id_s ',' enum_id
	'''
	if (len(p) == 2):
		p[0] = Node ('enum_id_s', None, p[1])
	else:
		p[0] = Node ('enum_id_s', [p[1].children,p[3]], p[0])

def p_enum_id(p):
	'''enum_id : IDENTIFIER
	   | CHAR
	'''
	p[0] = Node ('enum_id', None, p[1])
	
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
	p[0] = Node ('range_spec', None, p[1])
	
def p_range_spec_opt(p):
	'''range_spec_opt :
	   | range_spec
	'''
	if (len(p) > 1):
		p[0] = Node ('range_spec_opt', None, p[1])
	else:
		p[0] = Node ('range_spec_opt', None, p[0])

def p_real_type(p):
	'''real_type : float_type
	   | fixed_type
	'''
	p[0] = Node ('real_type', None, p[1])
	
def p_float_type(p):
	'''float_type : DIGITS expression range_spec_opt
	'''
	p[0] = Node ('float_type', [p[1],p[2],p[3]], p[0])
	
def p_fixed_type(p):
	'''fixed_type : DELTA expression range_spec
	   | DELTA expression DIGITS expression range_spec_opt
	'''
	if (len(p) == 4):
		p[0] = Node ('fixed_type', [p[2],p[3]], p[1])
	else:
		p[0] = Node ('fixed_type', [p[2],p[4],p[5]], p[1])

def p_array_type(p):
	'''array_type : unconstr_array_type
	   | constr_array_type
	'''
	p[0] = p[1]
	p[0].typ = 'array_type'
	
def p_unconstr_array_type(p):
	'''unconstr_array_type : ARRAY '(' index_s ')' OF component_subtype_def
	'''
	p[0] = Node ('unconstr_array_type', [p[3],p[6]], p[0], desig=p[1])
	
def p_constr_array_type(p):
	'''constr_array_type : ARRAY iter_index_constraint OF component_subtype_def
	'''
	p[0] = Node ('constr_array_type', [p[2],p[4]], p[0], desig=p[1])
	
def p_component_subtype_def(p):
	'''component_subtype_def : aliased_opt subtype_ind
	'''
	p[0] = Node ('component_subtype_def', [p[1],p[2]] ,p[0])
	
def p_aliased_opt(p):
	'''aliased_opt : 
	   | ALIASED
	'''
	if (len(p) > 1):
		p[0] = Node ('aliased_opt', None, None, desig=p[1])
	else:
		p[0] = Node ('aliased_opt', None, p[0])
	
def p_index_s(p):
	'''index_s : index
	   | index_s ',' index
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'index_s'
	else:
		p[1] = Node ('index_s', [p[1],p[3]], p[0])

def p_index(p):
	'''index : name RANGE BOX
	'''
	p[0] = Node ('index', [p[1],p[2],p[3]], p[0])
	
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
	'''record_type : tagged_opt limited_opt record_def
	'''
	p[0] = Node ('record_type', [p[1],p[2],p[3]], p[0])
	
def p_record_def(p):
	'''record_def : RECORD pragma_s comp_list END RECORD
	   | NuLL RECORD
	'''
	if (len(p) == 3):
		s = p[1] + ' ' + p[2]
		p[0] = Node ('record_def', None, p[0], s)
	else:
		p[0] = Node ('record_def', [p[2],p[3]], p[0], desig = p[1])
	
def p_tagged_opt(p):
	'''tagged_opt :
	   | TAGGED
	   | ABSTRACT TAGGED
	'''
	if (len(p) > 1):
		p[0] = Node ('tagged_opt', None, None, desig=p[1])
	else:
		p[0] = Node ('tagged_opt', None, p[0])

def p_comp_list(p):
	'''comp_list : comp_decl_s variant_part_opt
	   | variant_part pragma_s
	   | NuLL ';' pragma_s
	'''
	if (len(p) == 3):
		p[0] = Node ('comp_list', [p[1],p[2]], p[0])
	else:
		p[0] = Node ('comp_list', [p[1],p[3]], p[0])
	
def p_comp_decl_s(p):
	'''comp_decl_s : comp_decl
	   | comp_decl_s pragma_s comp_decl
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'comp_decl_s'
	else:
		p[0] = Node ('comp_decl_s', [p[1],p[2],p[3]], p[0])
	
def p_variant_part_opt(p):
	'''variant_part_opt : pragma_s
	   | pragma_s variant_part pragma_s
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'variant_part_opt'
	else:
		p[0] = Node ('variant_part_opt', [p[1],p[2],p[3]], p[0])
	
def p_comp_decl(p):
	'''comp_decl : def_id_s ':' component_subtype_def init_opt ';'
	   | error ';'
	'''
	if (len(p) == 3):
		p[0] = Node ('comp_decl', None, p[1])
	else:
		p[0] = Node ('comp_decl', [p[1],p[3],p[4]], p[2])
	
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
	'''discrim_spec : def_id_s ':' access_opt mark init_opt
	   | error
	'''
	p[0] = Node ('discrim_spec', [] ,p[2])

def p_access_opt(p):
	'''access_opt :
	   | ACCESS
	'''
	if (len(p) > 1):
		p[0] = Node ('access_opt', None, p[1])
	else:
		p[0] = Node ('access_opt', None, p[0])
	
def p_variant_part(p):
	'''variant_part : CASE simple_name IS pragma_s variant_s END CASE ';'
	'''
	p[0] = Node ('variant_part', [p[2],p[4],p[5]], p[1])
	
def p_variant_s(p):
	'''variant_s : variant
	   | variant_s variant
	'''
	if (len(p) == 2):
		p[0] = Node ('variant_s', None, p[1])
	else:
		p[0] = Node ('variant_s', [p[1].chidren,p[2]], p[0])
	
def p_variant(p):
	'''variant : WHEN choice_s ARROW pragma_s comp_list
	'''
	p[0] = Node ('variant', [p[2],p[4],p[5]], p[1])
	
def p_choice_s(p):
	'''choice_s : choice
	   | choice_s '|' choice
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'choice_s'
	else:
		p[0] = Node ('p_choice_s', [p[1], p[3]], p[0])
	
def p_choice(p):
	'''choice : expression
	   | discrete_with_range
	   | OTHERS
	'''
	if (p[1] == 'others'):
		p[0] = Node ('choice',None, None, desig = p[1])
	else:
		p[0] = p[1]
		p[0].typ = 'choice'
	
def p_discrete_with_range(p):
	'''discrete_with_range : name range_constraint
	   | range
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'discrete_with_range'
	else:
		p[0] = Node ('discrete_with_range', [p[1],p[2]], p[0])
	
def p_access_type(p):
	'''access_type : ACCESS subtype_ind
	   | ACCESS CONSTANT subtype_ind
	   | ACCESS ALL subtype_ind
	'''
	if (len(p) == 3):
		p[0] = Node ('access_type', [p[2]], p[0], desig=p[1])
	elif (len(p) == 4):
		p[0] = p[3]
		p[0].typ = 'access_type'
		p[0].desig = p[1] + ' ' + p[2]


def p_decl_part(p):
	'''decl_part :
	   | decl_item_or_body_s1
	'''
	if (len(p) > 1):
		p[0] = p[1]
		p[0].typ = 'decl_part'
	else:
		p[0] = Node ('decl_part', None, p[0])
	
def p_decl_item_s(p):
	'''decl_item_s : 
	   | decl_item_s1
	'''
	if (len(p) > 1):
		p[0] = Node('decl_item_s', None, p[1])
	else:
		p[0] = Node ('decl_item_s', None, p[0])
	
def p_decl_item_s1(p):
	'''decl_item_s1 : decl_item
	   | decl_item_s1 decl_item
	'''
	if (len(p) == 2):
		p[0] = Node ('decl_item_s1', None, p[1])
	else:
		p[0] = Node ('decl_item_s1', [p[1].children, p[2]], p[0])

def p_decl_item(p):
	'''decl_item : decl
	   | use_clause
	   | rep_spec
	   | pragma
	'''
	p[0] = p[1]
	p[0].typ = 'decl_item'

def p_decl_item_or_body_s1(p):
	'''decl_item_or_body_s1 : decl_item_or_body
	   | decl_item_or_body_s1 decl_item_or_body
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'decl_item_or_body_s1'
	else:
		p[0] = Node ('decl_item_or_body_s1', [p[1],p[2]], p[0])
	
def p_decl_item_or_body(p):
	'''decl_item_or_body : body
	   | decl_item
	'''
	p[0] = p[1]
	p[0].typ = 'decl_item_or_body'
	
def p_body(p):
	'''body : subprog_body
	   | pkg_body
	   | task_body
	   | prot_body
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
		p[0] = Node ('mark', [p[1],p[3]], p[0], desig=p[2])

def p_simple_name(p):
	'''simple_name : IDENTIFIER
	'''
	p[0] = Node('simple_name', None, None, desig=p[1])
	
def p_compound_name(p):
	'''compound_name : simple_name
	   | compound_name '.' simple_name
	'''
	if (len(p) == 2):
		p[0] = Node ('compound_name', None, p[1], p[1].desig)
	else:
		s = p[1].desig + '.' + p[3].desig
		p[0] = Node ('compound_name', p[1].children+[p[3]], p[0], s)	
	
def p_c_name_list(p):
	'''c_name_list : compound_name
	    | c_name_list ',' compound_name
	'''
	if (len(p) == 2):
		p[0] = Node ('c_name_list', None, p[1], p[1].desig)
	else:
		s = p[1].desig + ', ' + p[3].desig
		p[0] = Node ('c_name_list', [p[1],p[3]], p[0], s)
	
def p_used_char(p):
	'''used_char : CHAR
	'''
	p[0] = Node('used_char', None, p[1])
	
def p_operator_symbol(p):
	'''operator_symbol : STRING
	'''
	p[0] = Node('operator_symbol', None, None, desig=p[1])
	
def p_indexed_comp(p):
	'''indexed_comp : name '(' value_s ')'
	'''
	# print (p[1],p[3])
	s = str(p[1].desig) + '(' + str(p[3].desig) + ')'
	p[0] = Node ('indexed_comp', [p[1],p[3]], p[0], desig=s)
	
def p_value_s(p):
	'''value_s : value
	   | value_s ',' value
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'value_s'
	else:
		s = str(p[1].desig) + ',' + str(p[3].desig)
		p[0] = Node ('value_s', [p[1],p[3]], p[0], desig=s)

def p_value(p):
	'''value : expression
	   | comp_assoc
	   | discrete_with_range
	   | error
	'''
	p[0] = p[1]
	p[1].typ = 'value'
	# p[0] = Node('value', None, p[0], desig=p[1].desig)
	
def p_selected_comp(p):
	'''selected_comp : name '.' simple_name
	   | name '.' used_char
	   | name '.' operator_symbol
	   | name '.' ALL
	'''
	s = p[1].desig + '.' + p[3].desig
	p[0] = Node('selected_comp', p[1].children+[p[3]], p[0], desig=s)
	
def p_attribute(p):
	'''attribute : name TICK attribute_id
	'''
	p[0] = Node ('attribute', [p[1],p[3]], p[0], desig=p[2])
	
def p_attribute_id(p):
	'''attribute_id : IDENTIFIER
	   | DIGITS
	   | DELTA
	   | ACCESS
	'''
	p[0] = Node('attribute_id', None, None, desig=p[1])
	
def p_literal(p):
	'''literal : INT
       | FLOAT
	   | NuLL
	'''
	p[0] = Node('literal', None, None, desig=p[1])
	
def p_aggregate(p):
	'''aggregate : '(' comp_assoc ')'
	   | '(' expression WITH value_s ')'
	   | '(' expression WITH NuLL RECORD ')'
	   | '(' NuLL RECORD ')'
	'''
	p[0] = p[2]
	p[2].typ = 'aggregate'
	
def p_comp_assoc(p):
	'''comp_assoc : choice_s ARROW expression
	'''
	p[0] = Node ('comp_assoc', [p[1],p[3]], p[0], desig=p[2])
	
def p_expression(p):
	'''expression : relation
	   | expression logical relation
	   | expression short_circuit relation
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
	p[0] = Node('logical', None, p[0], desig=p[1])
	
def p_short_circuit(p):
	'''short_circuit : AND THEN
	   | OR ELSE
	'''
	p[0] = Node ('short_circuit', None, p[0], desig=p[1]+' '+p[2])
	
def p_relation(p):
	'''relation : simple_expression
	   | simple_expression relational simple_expression
	   | simple_expression membership range
	   | simple_expression membership name
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'relation'
	else:
		p[0] = Node ('relation', [p[1],p[3]], p[0], desig=p[2].desig)
	
def p_relational(p):
	'''relational : '='
	   | NEQ
	   | '<'
	   | LEQ
	   | '>'
	   | GEQ
	'''
	p[0] = Node('relational', None, None, desig=p[1])

def p_membership(p):
	'''membership : IN
	   | NOT IN
	'''
	p[0] = Node('membership', None, None, desig=p[2])	
	
def p_simple_expression(p):
	'''simple_expression : unary term
	   | term
	   | simple_expression adding term
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'simple_expression'
	elif (len(p) == 3):
		p[0] = Node ('simple_expression', [p[1],p[2]], p[0])
	else:
		p[0] = Node ('simple_expression', [p[1],p[3]], p[0], desig=p[2].desig)

def p_unary(p):
	'''unary   : '+'
	   | '-'
	'''
	p[0] = Node('unary', None, None, desig=p[1])

def p_adding(p):
	'''adding  : '+'
	   | '-'
	   | '&'
	'''
	p[0] = Node('adding', None, None, desig=p[1])
	
def p_term(p):
	'''term    : factor
	   | term multiplying factor
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'term'
	else:
		p[0] = Node ('term', [p[1],p[3]], p[0], desig=p[2].desig)
	
def p_multiplying(p):
	'''multiplying : '*'
	   | '/'
	   | MOD
	   | REM
	   | STARSTAR
	'''
	p[0] = Node('multiplying', None, None, desig=p[1])
	
def p_factor(p):
	'''factor : primary
	   | NOT primary
	   | ABS primary
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'factor'
	else:
		p[0] = Node ('factor', [p[2]], p[0], desig=p[1])

def p_primary(p):
	'''primary : literal
	   | name
	   | allocator
	   | qualified
	   | parenthesized_primary
	'''
	# print (p[1].typ)
	p[0] = p[1]
	p[0].typ = 'primary'
	
def p_parenthesized_primary(p):
	'''parenthesized_primary : aggregate
	   | '(' expression ')'
	'''
	if (len(p) == 2):
		p[0] = Node ('parenthesized_primary', None, p[1])
	else:
		p[0] = Node ('parenthesized_primary', None, p[2])
	
def p_qualified(p):
	'''qualified : name TICK parenthesized_primary
	'''
	p[0] = Node ('qualified', [p[1],p[3]], p[2])
	
def p_allocator(p):
	'''allocator : NEW name
	   | NEW qualified
	'''
	p[0] = Node ('allocator', [p[2]], p[1])
	
def p_statement_s(p):
	'''statement_s : statement
	   | statement_s statement
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'statement_s'
		# print ('ssss')
	else:
		p[0] = Node ('statement_s', [p[1],p[2]], p[0])
	
def p_statement(p):
	'''statement : unlabeled
	   | label statement
	'''
	if (len(p) == 2):
		p[0] = p[1]
		# print (p[0].children)
	else:
		p[0] = Node ('statement', [p[1]]+p[2].children, p[0])
	
def p_unlabeled(p):
	'''unlabeled : simple_stmt
	   | compound_stmt
	'''
	# | pragma
	p[0] = p[1]
	p[0].typ = 'unlabeled'

def p_simple_stmt(p):
	'''simple_stmt : null_stmt
	   | assign_stmt
	   | exit_stmt
	   | return_stmt
	   | procedure_call
	   | delay_stmt
	   | abort_stmt
	   | raise_stmt
	   | code_stmt
	   | requeue_stmt
	   | error ';'
	'''
	p[0] = p[1]
	p[0].typ = 'simple_stmt'
	# print (p[0].desig)

def p_compound_stmt(p):
	'''compound_stmt : if_stmt
	   | case_stmt	
	   | loop_stmt
	   | block
	   | accept_stmt
	   | select_stmt
	'''
	p[0] = p[1]
	p[0].typ = 'compound_stmt'

def p_label(p):
	'''label : LL IDENTIFIER RR
	'''
	p[0] = Node('label', None, None, desig=p[1]+p[2]+p[3])
	
def p_null_stmt(p):
	'''null_stmt : NuLL ';'
	'''
	p[0] = Node('null_stmt', None, p[1])
	
def p_assign_stmt(p):
	'''assign_stmt : name ASSIGN expression ';'
	'''
	p[0] = Node ('assign_stmt', [p[1],p[3]], p[0], desig=p[2])
	
def p_if_stmt(p):
	'''if_stmt : IF cond_clause_s else_opt END IF ';'
	'''
	p[0] = Node ('if_stmt', [p[2],p[3]], p[0], desig=p[1])
	
def p_cond_clause_s(p):
	'''cond_clause_s : cond_clause
	   | cond_clause_s ELSIF cond_clause
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'cond_clause_s'
		p[0].desig = 'no_elsif'
	else:
		p[0] = Node ('cond_clause_s', [p[1],p[3]], p[0], desig=p[2])

def p_cond_clause(p):
	'''cond_clause : cond_part statement_s
	'''
	p[0] = Node ('cond_clause', [p[1],p[2]], p[0])
	
def p_cond_part(p):
	'''cond_part : condition THEN
	'''
	p[0] = Node ('cond_part', [p[1]], p[0], desig=p[2])
	
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
		p[0] = p[2]
		p[0].desig = p[1]
		p[0].typ = 'else_opt'
	else:
		p[0] = Node ('else_opt', None, p[0])

	
def p_case_stmt(p):
	'''case_stmt : case_hdr pragma_s alternative_s END CASE ';'
	'''
	p[0] = Node ('case_stmt', [p[1],p[2],p[3]], p[0], desig=p[5])

def p_case_hdr(p):
	'''case_hdr : CASE expression IS
	'''
	p[0] = p[2]
	p[2].typ = 'case_hdr'
	p[2].desig = p[1]
	
def p_alternative_s(p):
	'''alternative_s :
	   | alternative_s alternative
	'''
	if (len(p) > 1):
		p[0] = Node ('alternative_s', [p[1],p[2]], p[0])	
	else:
		p[0] = Node ('alternative_s', None, p[0])
	
def p_alternative(p):
	'''alternative : WHEN choice_s ARROW statement_s
	'''
	p[0] = Node ('alternative', [p[2],p[4]], p[0], desig=p[1])
	
def p_loop_stmt(p):
	'''loop_stmt : label_opt iteration basic_loop id_opt ';'
	'''
	p[0] = Node ('loop_stmt', [p[1],p[2],p[3],p[4]], p[0], desig='LOOP_STMT')
	
def p_label_opt(p):
	'''label_opt :
	   | IDENTIFIER ':'
	'''
	if (len(p) > 1):
		p[0] = Node ('label_opt', None, None, desig=p[1])
	else:
		p[0] = Node ('label_opt', None, p[0])

def p_iteration(p):
	'''iteration :
	   | WHILE condition
	   | iter_part reverse_opt discrete_range
	'''
	if (len(p) == 3):
		p[0] = Node ('iteration', [p[2]], p[0], desig=p[1])
	elif (len(p) == 4):
		p[0] = Node ('iteration', [p[1],p[2],p[3]], p[0])
	else:
		p[0] = Node ('iteration', None, p[0])
	
def p_iter_part(p):
	'''iter_part : FOR IDENTIFIER IN
	'''
	s = p[1] + ' ' + p[2]
	p[0] = Node ('iter_part', None, None, desig=s)
	
def p_reverse_opt(p):
	'''reverse_opt :
	   | REVERSE
	'''
	if (len(p) > 1):
		p[0] = Node ('reverse_opt', None, None, desig=p[1])
	else:
		p[0] = Node ('reverse_opt', None, p[0])
	
def p_basic_loop(p):
	'''basic_loop : LOOP statement_s END LOOP
	'''
	p[0] = Node ('basic_loop', [p[2]], p[0], desig=p[1])
	
def p_id_opt(p):
	'''id_opt :
	   | designator
	'''
	if (len(p) > 1):
		p[0] = Node ('id_opt', None, p[0], desig=p[1].desig)
	else:
		p[0] = Node ('id_opt', None, p[0])

def p_block(p):
	'''block : label_opt block_decl block_body END id_opt ';'
	'''
	p[0] = Node ('block', [p[1],p[2],p[3]], p[5])
	
def p_block_decl(p):
	'''block_decl :
	   | DECLARE decl_part
	'''
	if (len(p) > 1):
		p[0] = Node ('block_decl', [p[2]], p[0], desig=p[1])
	else:
		p[0] = Node ('block_decl', None, p[0])
	
def p_block_body(p):
	'''block_body : BEGIN handled_stmt_s
	'''
	p[0] = Node ('block_body', [p[2]], p[0], desig=p[1])
	
def p_handled_stmt_s(p):
	'''handled_stmt_s : statement_s except_handler_part_opt 
	'''
	p[0] = Node ('handled_stmt_s', [p[1],p[2]], p[0])
	
def p_except_handler_part_opt(p):
	'''except_handler_part_opt :
	   | except_handler_part
	'''
	if (len(p) > 1):
		p[0] = p[1]
		p[0].typ = 'except_handler_part_opt'
	else:
		p[0] = Node ('except_handler_part_opt', None, p[0])
	
def p_exit_stmt(p):
	'''exit_stmt : EXIT name_opt when_opt ';'
	'''
	p[0] = Node ('exit_stmt', [p[2],p[3]], p[1])
	
def p_name_opt(p):
	'''name_opt :
	   | name
	'''
	if (len(p) > 1):
		p[0] = Node ('name_opt', None, p[1])
	else:
		p[0] = Node ('name_opt', None, p[0])
	
def p_when_opt(p):
	'''when_opt :
	   | WHEN condition
	'''
	if (len(p) > 1):
		p[0] = Node ('when_opt', [p[2]], p[1])
	else:
		p[0] = Node ('when_opt', None, p[0])
	
def p_return_stmt(p):
	'''return_stmt : RETURN ';'
	   | RETURN expression ';'
	'''
	if (len(p) == 2):
		p[0] = Node ('return_stmt', None, None, desig=p[1])
	else:
		p[0] = Node ('return_stmt', [p[2]], p[0], desig=p[1])


def p_subprog_decl(p):
	'''subprog_decl : subprog_spec ';'
	   | generic_subp_inst ';'
	   | subprog_spec_is_push ABSTRACT ';'
	'''
	p[0] = Node ('subprog_decl', None, p[1])
	
def p_subprog_spec(p):
	'''subprog_spec : PROCEDURE compound_name formal_part_opt
	   | FUNCTION designator formal_part_opt RETURN name
	   | FUNCTION designator
	'''
	if (len(p) == 3):
		p[0] = Node ('subprog_spec', [p[2]], p[0], desig=p[1])
	elif (len(p) == 6):
		# print (p[2].desig,p[3].desig,p[5].desig)
		# print (p[3].children)
		p[0] = Node ('subprog_spec', [p[2],p[3],p[5]], p[0], desig=p[1])
	else:
		p[0] = Node ('subprog_spec', [p[2],p[3]], p[0], desig=p[1])
	
def p_designator(p):
	'''designator : compound_name
	   | STRING
	'''
	if (isinstance(p[1],str)):
		p[0] = Node('designator', None, None, p[1])
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
		p[0] = Node ('formal_part_opt', None, p[0])
	
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
	'''param : def_id_s ':' mode mark init_opt
	   | error
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'param'
	else:
		p[0] = Node ('param', [p[1],p[3],p[4],p[5]], p[0])
	
def p_mode(p):
	'''mode :
	   | IN
	   | OUT
	   | IN OUT
	   | ACCESS
	'''
	if (len(p) == 1):
		p[0] = Node ('mode', None, p[0])
	elif (len(p) == 2):
		p[0] = Node ('mode', None, None, desig=p[1])
	else:
		s = p[1] + ' ' + p[2]
		p[0] = Node ('mode', None, None, desig=s)
	
def p_subprog_spec_is_push(p):
	'''subprog_spec_is_push : subprog_spec IS
	'''
	p[0] = Node ('subprog_spec_is_push', [p[1]], p[0], desig='IS')
	
def p_subprog_body(p):
	'''subprog_body : subprog_spec_is_push decl_part block_body END id_opt ';'
	'''
	p[0] = Node ('subprog_body', [p[1],p[2],p[3],p[5]], p[0])
	
def p_procedure_call(p):
	'''procedure_call : name ';'
	'''
	p[0] = p[1]
	p[0].typ = 'procedure_call'
	# p[0] = Node ('procedure_call', None, p[1], desig=p[1].desig+'.__procedure__')
	
def p_pkg_decl(p):
	'''pkg_decl : pkg_spec ';'
	   | generic_pkg_inst ';'
	'''
	p[0] = Node ('pkg_decl', None, p[1])
	
def p_pkg_spec(p):
	'''pkg_spec : PACKAGE compound_name IS decl_item_s private_part END c_id_opt
	'''
	p[0] = Node ('pkg_spec', [p[2],p[4],p[5],p[7]], p[1])
	
def p_private_part(p):
	'''private_part :
	   | PRIVATE decl_item_s
	'''
	if (len(p) > 1):
		p[0] = Node ('private_type', [p[2]], p[1])
	else:
		p[0] = Node ('private_type', None, p[0])
	
def p_c_id_opt(p):
	'''c_id_opt : 
	   | compound_name
	'''
	if (len(p) > 1):
		p[0] = Node('p_c_id_opt', None, p[1])
	else:
		p[0] = Node ('p_c_id_opt', None, p[0])
	
def p_pkg_body(p):
	'''pkg_body : PACKAGE BODY compound_name IS decl_part body_opt END c_id_opt ';'
	'''
	p[0] = Node ('pkg_body', [p[2],p[3],p[5],p[7]], p[1])
	
def p_body_opt(p):
	'''body_opt :
	   | block_body
	'''
	if (len(p) > 1):
		p[0] = Node('body_opt', None, p[1])
	else:
		p[0] = Node ('body_opt', None, p[0])
	
def p_private_type(p):
	'''private_type : tagged_opt limited_opt PRIVATE
	'''
	p[0] = Node ('private_type', [p[1],p[2]], p[3])
	
def p_limited_opt(p):
	'''limited_opt :
	   | LIMITED
	'''
	if (len(p) > 1):
		p[0] = Node('limited_opt', None, None, desig=p[1])
	else:
		p[0] = Node ('limited_opt', None, p[0])
	
def p_use_clause(p):
	'''use_clause : USE name_s ';'
	   | USE TYPE name_s ';'
	'''
	if (len(p) == 4):
		p[0] = Node('use_clause',[p[2]],p[0], desig='USE')
	else:
		p[0] = Node('use_clause',[p[3]],p[0], desig='USE TYPE')
	
def p_name_s(p):
	'''name_s : name
	   | name_s ',' name
	'''
	if (len(p) == 2):
		p[0] = p[1]
		p[0].typ = 'name_s'
		# p[0] = Node ('name_s', None, p[1], p[1].desig)
	else:
		s = p[1].desig + ', ' + p[3].desig
		p[0] = Node ('name_s', p[1].children + [p[3]], p[0], s)
	
def p_rename_decl(p):
	'''rename_decl : def_id_s ':' object_qualifier_opt subtype_ind renames ';'
	   | def_id_s ':' EXCEPTION renames ';'
	   | rename_unit
	'''
	if (len(p) == 2):
		p[0] = Node('rename_decl',None,p[1])
	elif (len(p) == 6):
		p[0] = Node('rename_decl', [p[1],p[3],p[4]],p[2])
	else:
		p[0] = Node ('rename_decl', [p[1],p[3],p[4],p[5]], p[2])

	
def p_rename_unit(p):
	'''rename_unit : PACKAGE compound_name renames ';'
	   | subprog_spec renames ';'
	   | generic_formal_part PACKAGE compound_name renames ';'
	   | generic_formal_part subprog_spec renames ';'
	'''
	if(len(p)==5):
		if(p[1]=='PACKAGE'):
			p[0]= Node('rename_unit',[p[1],p[2],p[3]],p[0])
		else:
			p[0]=Node('rename_unit',[p[1],p[2]],p[0])
	elif (len(p)==4):
		p[0]=Node('rename_unit',[p[1],p[2]],p[0])
	elif(len(p)==6):
		p[0]=Node('rename_unit',[p[1],p[2],p[3],p[4]],p[0])


def p_renames(p):
	'''renames : RENAMES name
	'''
	p[0] = Node('renames',[p[2]],p[1])
def p_task_decl(p):
	'''task_decl : task_spec ';'
	'''
	p[0] = Node('task_decl',None,p[1])
	
def p_task_spec(p):
	'''task_spec : TASK simple_name task_def
	   | TASK TYPE simple_name discrim_part_opt task_def
	'''
	if(len(p)==4):
		p[0] = Node('task_spec',[p[2],p[3]],p[1])
	
def p_task_def(p):
	'''task_def :
	   | IS entry_decl_s rep_spec_s task_private_opt END id_opt
	'''
	p[0]=Node('task_def',[p[2],p[3],p[4],p[6]],p[0])
	
def p_task_private_opt(p):
	'''task_private_opt :
	   | PRIVATE entry_decl_s rep_spec_s
	'''
	if(len(p)>1):
		p[0] = Node('task_private_opt',[p[2],p[3]],p[1])
	else:
		p[0] = Node ('task_private_opt', None, p[0])
	
def p_task_body(p):
	'''task_body : TASK BODY simple_name IS decl_part block_body END id_opt ';'
	'''
	p[0]=Node('task_body',[p[3],p[5],p[6],p[8]],p[1])
	
def p_prot_decl(p):
	'''prot_decl : prot_spec ';'
	'''
	p[0]=Node('prot_decl',None,p[1])
	
def p_prot_spec(p):
	'''prot_spec : PROTECTED IDENTIFIER prot_def
	   | PROTECTED TYPE simple_name discrim_part_opt prot_def
	'''
	if(len(p)==4):
		p[0]=Node('prot_spec',[p[2],p[3]],p[1])
	else:
		p[0]=Node('prot_spec',[p[2],p[3],p[4],p[5]],p[1])

def p_prot_def(p):
	'''prot_def : IS prot_op_decl_s prot_private_opt END id_opt
	'''
	p[0]=Node('prot_def',[p[2],p[3],p[5]],p[0])

	
def p_prot_private_opt(p):
	'''prot_private_opt :
	   | PRIVATE prot_elem_decl_s 
	'''
	if(len(p)>1):
		p[0]=Node('prot_private_opt',[p[2]],p[1])
	else:
		p[0] = Node ('prot_private_opt', None, p[0])

def p_prot_op_decl_s(p):
	'''prot_op_decl_s : 
	   | prot_op_decl_s prot_op_decl
	'''
	if(len(p)>1):
		p[0]=Node('prot_op_decl_s',[p[1].children,p[2]],p[0])
	else:
		p[0] = Node ('prot_op_decl_s', None, p[0])

	
def p_prot_op_decl(p):
	'''prot_op_decl : entry_decl
	   | subprog_spec ';'
	   | rep_spec
	   | pragma
	'''
	p[0] = Node ('prot_op_decl', None, p[1])
	
def p_prot_elem_decl_s(p):
	'''prot_elem_decl_s : 
	   | prot_elem_decl_s prot_elem_decl
	'''
	if (len(p) > 1):
		p[0] = Node ('prot_elem_decl_s', [p[1].chidlren,p[2]], p[0])
	else:
		p[0] = Node ('prot_elem_decl_s', None, p[0])
	
def p_prot_elem_decl(p):
	'''prot_elem_decl : prot_op_decl 
    | comp_decl
	'''
	
def p_prot_body(p):
	'''prot_body : PROTECTED BODY simple_name IS prot_op_body_s END id_opt ';'
	'''
	p[0] = Node ('prot_body', [p[3],p[5],p[7]], p[1])
	
def p_prot_op_body_s(p):
	'''prot_op_body_s : pragma_s
	   | prot_op_body_s prot_op_body pragma_s
	'''
	if (len(p) == 2):
		p[0] = Node ('prot_op_body_s', None, p[1])
	else:
		p[0] = Node ('prot_op_body_s', [p[1].chidlren,p[2]], p[0])
	
def p_prot_op_body(p):
	'''prot_op_body : entry_body
	   | subprog_body
	   | subprog_spec ';'
	'''
	p[0] = p[1]
	p[0].typ = 'prot_op_body'
	
def p_entry_decl_s(p):
	'''entry_decl_s : pragma_s
	   | entry_decl_s entry_decl pragma_s
	'''
	if (len(p) == 2):
		p[0] = Node ('entry_decl_s', None, p[1])
	else:
		p[0] = Node ('entry_decl_s', [p[1].chidlren,p[2],p[3]], p[0])

def p_entry_decl(p):
	'''entry_decl : ENTRY IDENTIFIER formal_part_opt ';'
	   | ENTRY IDENTIFIER '(' discrete_range ')' formal_part_opt ';'
	'''
	if (len(p) == 5):
		p[0] = Node ('entry_decl', [p[2],p[3]], p[1])
	else:
		p[0] = Node ('entry_decl', [p[2],p[4],p[6]], p[1])
	
def p_entry_body(p):
	'''entry_body : ENTRY IDENTIFIER formal_part_opt WHEN condition entry_body_part
	   | ENTRY IDENTIFIER '(' iter_part discrete_range ')' formal_part_opt WHEN condition entry_body_part
	'''
	if (len(p) == 7):
		p[0] = Node ('entry_body', [p[2],p[3],p[5],p[6]], p[1])
	else:
		p[0] = Node ('entry_body', [p[2],p[4],p[5],p[7],p[9],p[10]], p[1])
	
def p_entry_body_part(p):
	'''entry_body_part : ';'
	   | IS decl_part block_body END id_opt ';'
	'''
	if (len(p) > 2):
		p[0] = Node ('entry_body_part', [p[2],p[3],p[5]], p[0])
	else:
		p[0] = Node ('entry_body_part', None, p[0])
	
def p_rep_spec_s(p):
	'''rep_spec_s :
	   | rep_spec_s rep_spec pragma_s
	'''
	if (len(p) > 1):
		p[0] = Node ('rep_spec_s', [p[1].children,p[2],p[3]], p[0])
	else:
		p[0] = Node ('rep_spec_s', None, p[0])
	
def p_entry_call(p):
	'''entry_call : procedure_call
	'''
	p[0] = Node('entry_call', None, p[1])
	
def p_accept_stmt(p):
	'''accept_stmt : accept_hdr ';'
	   | accept_hdr DO handled_stmt_s END id_opt ';'
	'''
	if (len(p) == 2):
		p[0] = Node ('accept_stmt', None, p[1])
	else:
		p[0] = Node ('accept_stmt', [p[2],p[3],p[4],p[5]], p[1])
	
def p_accept_hdr(p):
	'''accept_hdr : ACCEPT entry_name formal_part_opt
	'''
	p[0] = Node('accept_hdr', [p[2],p[3]], p[1])
	
def p_entry_name(p):
	'''entry_name : simple_name
	   | entry_name '(' expression ')'
	'''
	if (len(p) == 2):
		p[0] = Node('entry_name', None, p[1])
	else:
		Node('entry_name', None, p[3])
	
def p_delay_stmt(p):
	'''delay_stmt : DELAY expression ';'
	   | DELAY UNTIL expression ';'
	'''
	if (len(p) == 4):
		p[0] = Node ('delay_stmt', [p[2]], p[1])
	else:
		p[0] = Node ('delay_stmt', [p[2],p[3]], p[1])
	
def p_select_stmt(p):
	'''select_stmt : select_wait
	   | async_select
	   | timed_entry_call
	   | cond_entry_call
	'''
	p[0] = Node ('select_stmt', None, p[1])
	
def p_select_wait(p):
	'''select_wait : SELECT guarded_select_alt or_select else_opt  END SELECT ';'
	'''
	p[0] = Node ('select_wait', [p[2],p[3]], p[1])
	
def p_guarded_select_alt(p):
	'''guarded_select_alt : select_alt
	   | WHEN condition ARROW select_alt
	'''
	if (len(p) == 2):
		p[0] = Node ('guarded_select_alt', None, p[1])
	else:
		p[0] = Node ('guarded_select_alt', [p[2],p[4]], p[1])
	
def p_or_select(p):
	'''or_select :
	   | or_select OR guarded_select_alt
	'''
	if (len(p) > 1):
		p[0] = Node ('or_select', [p[1].children,p[2],p[3]], p[0])
	else:
		p[0] = Node ('or_select', None, p[0])

	
def p_select_alt(p):
	'''select_alt : accept_stmt stmts_opt
	   | delay_stmt stmts_opt
	   | TERMINATE ';'
	'''
	if(p[2]!=';'):
		p[0] = Node('select_alt',[p[1],p[2]],p[0])
	else:
		p[0] = Node('select_alt', None,p[1])

	
def p_delay_or_entry_alt(p):
	'''delay_or_entry_alt : delay_stmt stmts_opt
	   | entry_call stmts_opt
	'''
	p[0] = Node('delay_or_entry_alt',[p[1],p[2]],p[0])
def p_async_select(p):
	'''async_select : SELECT delay_or_entry_alt THEN ABORT statement_s END SELECT ';'
	'''
	p[0] = Node('async_select',[p[2],p[5]],p[1])
def p_timed_entry_call(p):
	'''timed_entry_call : SELECT entry_call stmts_opt OR delay_stmt stmts_opt END SELECT ';'
	'''
	p[0] = Node('timed_entry_call',[p[2],p[3],p[5],p[6]],p[1])
def p_cond_entry_call(p):
	'''cond_entry_call : SELECT entry_call stmts_opt ELSE statement_s END SELECT ';'
	'''
	p[0] = Node('cond_entry_call',[p[2],p[3],p[5]],p[1])
	
def p_stmts_opt(p):
	'''stmts_opt :
	   | statement_s
	'''
	if (len(p) > 1):
		p[0] = Node('stmts_opt', None, p[1])
	else:
		p[0] = Node ('stmts_opt', None, p[0])
	
def p_abort_stmt(p):
	'''abort_stmt : ABORT name_s ';'
	'''
	p[0] = Node('abort_stmt', [p[2]], p[1])
	
def p_compilation(p):
	'''compilation :
	   | compilation comp_unit
	   | pragma pragma_s
	'''
	if(len(p) > 1):
		if (p[1].typ == 'compilation'):
			p[0] = Node('compilation', [p[1].children,p[2]], p[0])
		else:
			p[0] = Node ('compilation', [p[1],p[2].children], p[0])
	else:
		p[0] = Node ('compilation', None, p[0])
	
def p_comp_unit(p):
	'''comp_unit : context_spec private_opt unit pragma_s
	   | private_opt unit pragma_s
	'''
	if(len(p)==4):
		p[0] = Node('comp_unit',[p[1],p[2],p[3]],p[0])
	else:
		p[0] = Node('comp_unit',[p[1],p[2],p[3],p[4]],p[0])
	
def p_private_opt(p):
	'''private_opt :
	   | PRIVATE
	'''
	if (len(p) > 1):
		p[0] = Node('private_opt', None, p[1])
	else:
		p[0] = Node ('private_opt', None, p[0])
	
def p_context_spec(p):
	'''context_spec : with_clause use_clause_opt
	   | context_spec with_clause use_clause_opt
	   | context_spec pragma
	''' 
	if(len(p) == 3 and p[1].typ == 'with_clause'):
		p[0] = Node('context_spec',[p[1],p[2]],p[0])
	elif(len(p)==3):
		p[0] = Node('context_spec',[p[1].children,p[2]],p[0])
	else:
		p[0] = Node('context_spec',[p[1].children,p[3]],p[0])
	
def p_with_clause(p):
	'''with_clause : WITH c_name_list ';'
	'''
	p[0] = Node('with_clause',[p[2]],p[0],desig=p[1])
	
def p_use_clause_opt(p):
	'''use_clause_opt :
	   | use_clause_opt use_clause
	'''
	if (len(p)>1):
		p[0] = Node('use_clause_opt',[p[1].children,p[2]],p[0])
	else:
		p[0] = Node ('use_clause_opt', None, p[0])
	
def p_unit(p):
	'''unit : pkg_decl
	   | pkg_body
	   | subprog_decl
	   | subprog_body
	   | subunit
	   | generic_decl
	   | rename_unit
	'''
	p[0] = Node('unit', [p[1]], p[0], desig='UNIT')

def p_subunit(p):
	'''subunit : SEPARATE '(' compound_name ')' subunit_body
	'''
	p[0] = Node('subunit',[p[3],p[5]], p[0], desig='SEPARATE')

def p_subunit_body(p):
	'''subunit_body : subprog_body
	   | pkg_body
	   | task_body
	   | prot_body
	'''
	p[0] = Node('subunit_body', None,p[1])
def p_body_stub(p):
	'''body_stub : TASK BODY simple_name IS SEPARATE ';'
	   | PACKAGE BODY compound_name IS SEPARATE ';'
	   | subprog_spec IS SEPARATE ';'
	   | PROTECTED BODY simple_name IS SEPARATE ';'
	'''
	if(p[1]=='TASK'):
		p[0] = Node('body_stub',[p[3]],p[1])
	elif(p[1]=='PACKAGE'):
		p[0] = Node('body_stub',[p[3]],p[1])
	elif(p[1]=='PROTECTED'):
		p[0] = Node('body_stub',[p[3]],p[1])
	else:
		p[0] = Node('body_stub',None,p[1])
	
def p_exception_decl(p):
	'''exception_decl : def_id_s ':' EXCEPTION ';'
	'''
	p[0] = Node('exception_decl', [p[1]], p[3])
	
def p_except_handler_part(p):
	'''except_handler_part : EXCEPTION exception_handler
	   | except_handler_part exception_handler
	'''
	if (isinstance(p[1],str)):
		p[0] = Node('except_handler_part',[p[2]],p[0],desig=p[1])
	else:
		p[0] = Node('except_handler_part',[p[1],p[2]],p[0])

	
def p_exception_handler(p):
	'''exception_handler : WHEN except_choice_s ARROW statement_s
	   | WHEN IDENTIFIER ':' except_choice_s ARROW statement_s
	'''
	if(len(p)==5):
		p[0] = Node('exception_handler',[p[2],p[4]],p[0],desig = p[1])
	else:
		s = p[1] + ' ' + p[2]
		p[0] = Node('exception_handler',[p[4],p[6]],p[0],desig = s)
	
def p_except_choice_s(p):
	'''except_choice_s : except_choice
	   | except_choice_s '|' except_choice
	'''
	if(len(p)==2):
		p[0]=p[1]
		p[0].typ = 'except_choice_s'
		# p[0] = Node('except_choice_s',None,p[1])
	else:
		p[0] = Node('except_choice_s',[p[1],p[3]],p[0])
	
def p_except_choice(p):
	'''except_choice : name
	   | OTHERS
	'''
	if (isinstance(p[1],str)):
		p[0] = Node('except_choice',None,None,desig=p[1])
	else:
		p[0] = p[1]
		p[1].typ = 'except_choice'
	
def p_raise_stmt(p):
	'''raise_stmt : RAISE name_opt ';'
	'''
	p[0] = Node('raise_stmt',[p[2]],p[1])
	
def p_requeue_stmt(p):
	'''requeue_stmt : REQUEUE name ';'
	   | REQUEUE name WITH ABORT ';'
	'''
	if(len(p)==3):
		p[0] = Node('requeue_stmt',[p[2]],p[1])	
	else:
		p[0] = Node('requeue_stmt',[p[2],p[4]],p[1])	
	
def p_generic_decl(p):
	'''generic_decl : generic_formal_part subprog_spec ';'
	   | generic_formal_part pkg_spec ';'
	'''
	p[0] = Node('generic_decl',[p[1],p[2]],p[0])
	
def p_generic_formal_part(p):
	'''generic_formal_part : GENERIC
	   | generic_formal_part generic_formal
	'''
	if(len(p)==2):
		p[0] = Node('generic_formal_part', None,p[1])
	else:
		p[0] = Node('generic_formal_part',[p[1].children,p[2]],p[0])
	
def p_generic_formal(p):
	'''generic_formal : param ';'
	   | TYPE simple_name generic_discrim_part_opt IS generic_type_def ';'
	   | WITH PROCEDURE simple_name formal_part_opt subp_default ';'
	   | WITH FUNCTION designator formal_part_opt RETURN name subp_default ';'
	   | WITH PACKAGE simple_name IS NEW name '(' BOX ')' ';'
	   | WITH PACKAGE simple_name IS NEW name ';'
	   | use_clause
	'''
	if(len(p)==2):
		p[0] = Node('generic_formal',None,p[1])
	elif(len(p)==3):
		p[0] = Node('generic_formal',None,p[1])
	elif(p[1]=='TYPE'):
		p[0] = Node('generic_formal',[p[2],p[3],p[5]],p[1])
	elif(p[2]=='PROCEDURE'):
		p[0] = Node('generic_formal',[p[3],p[4],p[5]],p[2])
	elif(p[2]=='FUNCTION'):
		p[0] = Node('generic_formal',[p[3],p[4],p[6],p[7]],p[2])
	elif(p[2]=='PACKAGE' and len(p)==8):
		p[0] = Node('generic_formal',[p[3],p[6]],p[2])
	else:
		p[0] = Node('generic_formal',[p[3],p[6],p[8]],p[2])
		
def p_generic_discrim_part_opt(p):
	'''generic_discrim_part_opt :
	   | discrim_part
	   | '(' BOX ')'
	'''
	if (len(p) == 2):
		p[0] = Node ('generic_discrim_part_opt', None, p[1])
	elif (len(p) == 4):
		p[0] = Node('generic_discrim_part_opt', None, p[3])
	else:
		p[0] = Node ('generic_discrim_part_opt', None, p[0])

def p_subp_default(p):
	'''subp_default :
	   | IS name
	   | IS BOX
	'''
	if(len(p)>1):
		p[0] = Node('subp_default', None, p[2])
	else:
		p[0] = Node ('subp_default', None, p[0])
	
def p_generic_type_def(p):
	'''generic_type_def : '(' BOX ')'
	   | RANGE BOX
	   | MOD BOX
	   | DELTA BOX
	   | DELTA BOX DIGITS BOX
	   | DIGITS BOX
	   | array_type
	   | access_type
	   | private_type
	   | generic_derived_type
	'''
	if(p[1]=='('):
		p[0] = Node('generic_type_def',None,p[2])
	elif(p[1]=='RANGE'):
		p[0] = Node('generic_type_def',[p[2]],p[1])
	elif(p[1]=='MOD'):
		p[0] = Node('generic_type_def',[p[2]],p[1])
	elif(p[1]=='DELTA' and len(p)==3):
		p[0] = Node('generic_type_def',[p[2]],p[1])
	elif(p[1]=='DELTA' and p[3]=='DIGITS'):
		p[0] = Node('generic_type_def',[p[2],p[4]],p[1])
	elif(p[1]=='DIGITS'):
		p[0] = Node('generic_type_def',[p[2]],p[1])
	else:
		p[0] = Node('generic_type_def',None,p[1])

def p_generic_derived_type(p):
	'''generic_derived_type : NEW subtype_ind
	   | NEW subtype_ind WITH PRIVATE
	   | ABSTRACT NEW subtype_ind WITH PRIVATE
	'''
	if(len(p)==3):
		p[0] = Node('generic_derived_type',None,p[2])
	elif(len(p)==5):
		p[0] = Node('generic_derived_type',[p[2],p[4]],p[0])
	else:
		p[0] = Node('generic_derived_type',[p[3],p[5]],p[1])

def p_generic_subp_inst(p):
	'''generic_subp_inst : subprog_spec IS generic_inst
	'''
	p[0] = Node('generic_subp_inst', [p[1],p[3]], p[0])

def p_generic_pkg_inst(p):
	'''generic_pkg_inst : PACKAGE compound_name IS generic_inst
	'''
	p[0] = Node('generic_pkg_inst', [p[2],p[4]], p[1])

def p_generic_inst(p):
	'''generic_inst : NEW name
	'''
	p[0] = Node('generic_inst', None, p[2])

def p_rep_spec(p):
	'''rep_spec : attrib_def
	   | record_type_spec
	   | address_spec
	'''
	p[0] = Node('rep_spec', None, p[1])
	
def p_attrib_def(p):
	'''attrib_def : FOR mark USE expression ';'
	'''
	p[0] = Node('code_stmt', [p[2],p[4]], p[1])

def p_record_type_spec(p):
	'''record_type_spec : FOR mark USE RECORD align_opt comp_loc_s END RECORD ';'
	'''
	p[0] = Node('record_type_spec',[p[2],p[5],p[6]],p[1])
	
def p_align_opt(p):
	'''align_opt :
	   | AT MOD expression ';'
	'''
	if(len(p)>1):
		p[0] = Node('align_opt', [p[3]], p[2])
	else:
		p[0] = Node ('align_opt', None, p[0])
	
def p_comp_loc_s(p):
	'''comp_loc_s :
	   | comp_loc_s mark AT expression RANGE range ';'
	'''
	if(len(p)>1):
		p[0]= Node('comp_loc_s',[p[1],p[2],p[4],p[6]],p[0])
	else:
		p[0] = Node ('comp_loc_s', None, p[0])

def p_address_spec(p):
	'''address_spec : FOR mark USE AT expression ';'
	'''
	p[0] = Node('address_spec', [p[2],p[5]], p[1])
def p_code_stmt(p):
	'''code_stmt : qualified ';'
	'''
	p[0] = Node('code_stmt', None, p[1])

def p_error(p):
	print ('line :',p.lineno,'-parse issue at token:',p.type)
	parser.errok()