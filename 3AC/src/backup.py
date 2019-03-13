# http://www.adaic.org/resources/add_content/standards/95lrm/grammar9x.y

import sys, re, os, logging
from ply import lex, yacc
from copy import *
from Tokens import *

from symtab import SymbolTable
from ThreeAddrCode import ThreeAddrCode

ST = SymbolTable()
TAC = ThreeAddrCode()

def p_goal_symbol(p):
	'''goal_symbol : compilation
	'''
	ST.printTable()
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
	'''pragma_arg : expression
	   | simple_name ARROW expression
	'''	

def p_pragma_s(p):
	'''pragma_s :
	   | pragma_s pragma
	'''

def p_decl(p):
	'''decl : object_decl
	   | type_decl
	   | subtype_decl
	   | subprog_decl
	'''

def p_object_decl(p):
	'''object_decl : def_id_s ':' object_subtype_def ';'   
	'''
	def_id_s = p[1]
	for id in def_id_s:
		if (p[3]['what'] == 'array'):
			attr_dict = deepcopy(p[3])
			attr_dict['tag'] = id
			ST.insert (id, attr_dict)
		else:
			dtype = p[3]['tag']
			attr_dict = {'tag': id, 'what': 'var', 'type': dtype}
			ST.insert(id, attr_dict)

def p_def_id_s(p):
	'''def_id_s : def_id
	   | def_id_s ',' def_id
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_def_id(p):
	'''def_id  : IDENTIFIER
	'''
	p[0] = p[1]

def p_object_subtype_def(p):
	'''object_subtype_def : subtype_ind
	   | array_type
	'''
	p[0] = p[1]

def p_type_decl(p):
	'''type_decl : TYPE IDENTIFIER discrim_part_opt type_completion ';'
	'''

def p_discrim_part_opt(p):
	'''discrim_part_opt :
	   | discrim_part
	   | '(' BOX ')'
	'''
	
def p_type_completion(p):
	'''type_completion :
	   | IS type_def
	'''

def p_type_def(p):
	'''type_def : integer_type
	   | array_type
	   | record_type
	'''
	p[0] = p[1]
	
def p_subtype_decl(p):
	'''subtype_decl : SUBTYPE IDENTIFIER IS subtype_ind ';'
	'''

def p_subtype_ind(p):
	'''subtype_ind : name
	'''
	p[0] = p[1]
	
def p_range_constraint(p):
	'''range_constraint : RANGE range
	'''

def p_range(p):
	'''range : simple_expression DOTDOT simple_expression
	'''
	r_start = p[1]['tag'] if TAC.isDict(p[1]) else p[1]
	r_end = p[3]['tag'] if TAC.isDict(p[3]) else p[3]
	p[0] = {'r_start': r_start, 'r_end': r_end}
		
def p_integer_type(p):
	'''integer_type : range_spec
	   | MOD expression
	'''
	
def p_range_spec(p):
	'''range_spec : range_constraint
	'''

def p_array_type(p):
	'''array_type : constr_array_type
	'''
	p[0] = p[1]
	
def p_constr_array_type(p):
	'''constr_array_type : ARRAY iter_index_constraint OF component_subtype_def
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

def p_component_subtype_def(p):
	'''component_subtype_def : subtype_ind
	'''
	p[0] = p[1]

def p_iter_index_constraint(p):
	'''iter_index_constraint : '(' range_s ')'
	'''
	p[0] = p[2]
	
def p_range_s(p):
	'''range_s : range
	   | range_s ',' range
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]
	
def p_record_type(p):
	'''record_type : record_def
	'''
	
def p_record_def(p):
	'''record_def : RECORD pragma_s comp_list END RECORD
	   | NuLL RECORD
	'''

def p_comp_list(p):
	'''comp_list : NuLL ';' pragma_s
	'''
	
def p_discrim_part(p):
	'''discrim_part : '(' discrim_spec_s ')'
	'''
	
def p_discrim_spec_s(p):
	'''discrim_spec_s : discrim_spec
	   | discrim_spec_s ';' discrim_spec
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_discrim_spec(p):
	'''discrim_spec : def_id_s ':' mark
	'''

def p_decl_part(p):
	'''decl_part :
	   | decl_item_or_body_s
	'''

def p_decl_item(p):
	'''decl_item : decl
	   | use_clause
	   | pragma
	'''

def p_decl_item_or_body_s(p):
	'''decl_item_or_body_s : decl_item_or_body
	   | decl_item_or_body_s decl_item_or_body
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]
	
def p_decl_item_or_body(p):
	'''decl_item_or_body : body
	   | decl_item
	'''
	p[0] = p[1]
	
def p_body(p):
	'''body : subprog_body
	'''
	p[0] = p[1]

def p_name(p):
	'''name : simple_name
	   | indexed_comp
	   | selected_comp
	   | operator_symbol
	'''
	p[0] = p[1]
	
# Case 2 needs to be handled
def p_mark(p):
	'''mark : simple_name
	   | mark '.' simple_name
	'''
	if (len(p) == 2):
		p[0] = deepcopy(p[1])

# assumes that this identifier has been seen previously
def p_simple_name(p):
	'''simple_name : IDENTIFIER
	'''
	p[0] = ST.getAttrDict(p[1])
	
# to be handled
def p_compound_name(p):
	'''compound_name : simple_name
	   | compound_name '.' simple_name
	'''
	if (len(p) == 2):
		p[0] = p[1]
	
def p_c_name_list(p):
	'''c_name_list : compound_name
	    | c_name_list ',' compound_name
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_used_char(p):
	'''used_char : CHAR
	'''

def p_operator_symbol(p):
	'''operator_symbol : STRING
	'''

def p_indexed_comp(p):
    '''indexed_comp : name '(' value_s ')'
    '''
    p[0] = deepcopy(p[1])
    if (p[1]['what'] == 'array'):
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
        if(tp==None):
            t5 = TAC.newTemp('Integer',ST)
            TAC.emit(op='-',lhs=t5,op1=p[3][dim-1],op2=p[1]['r_start_s'][dim-1])
        else:
            t4 = TAC.newTemp('Integer',ST)
            TAC.emit(op='-',lhs=t4,op1=p[3][dim-1],op2=p[1]['r_start_s'][dim-1])
            t5 = TAC.newTemp('Integer',ST)
            TAC.emit(op='+',lhs=t5,op1=t4,op2=tp)
        t6 = TAC.newTemp('Integer',ST)
        TAC.emit(op='*',lhs=t6,op1=t5,op2=ST.table[p[1]['type']]['width'])
        # Need to care about base address later on
        p[0]['tag'] = p[1]['tag'] + '+' + t6

def p_value_s(p):
	'''value_s : value
	   | value_s ',' value
	'''
	p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

# Changed grammar from value : expression
def p_value(p):
	'''value : simple_expression
	'''
	p[0] = p[1]
	
def p_selected_comp(p):
	'''selected_comp : name '.' simple_name
	   | name '.' used_char
	   | name '.' operator_symbol
	   | name '.' ALL
	'''

def p_literal(p):
	'''literal : INT
	   | NuLL
	'''
	p[0] = {'tag' : p[1], 'type': 'Integer'}

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
		p[0] = deepcopy(p[4])
		temp_var = TAC.newTemp(p[1]['type'], ST)
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

# Changed grammar from relation : simple_expression | simple_expression relational simple_expression
def p_relation(p):
	'''relation : simple_expression relational simple_expression
	'''
	p[0] = {}
	p[0]['type'] = 'bool'
	p[0]['true_list'] = TAC.makeList(TAC.getLine() - 2)
	p[0]['false_list'] = TAC.makeList(TAC.getLine() - 1)
	TAC.emit(op='goto_' + p[2], op1=p[1], op2=p[3], lhs=None)
	
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
		p[0] = p[1]
	else:
		temp_var = TAC.newTemp(p[1]['type'], ST)
		p[0] = deepcopy(p[1])
		TAC.emit(op=p[2],lhs=temp_var,op1=p[1],op2=p[3])
		p[0]['tag'] = temp_var

def p_adding(p):
	'''adding  : '+'
	   | '-'
	   | '&'
	'''
	p[0] = p[1]
	
def p_term(p):
	'''term : factor
	   | term multiplying factor
	'''
	if (len(p) == 2):
		p[0] = p[1]
	else:
		temp_var = TAC.newTemp(p[1]['type'], ST)
		p[0] = deepcopy(p[1])
		TAC.emit(op=p[2],lhs=temp_var,op1=p[1],op2=p[3])
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
			| NOT primary
	'''
	if (len(p) == 2):
		p[0] = p[1]

def p_primary(p):
	'''primary : literal
	   | name
	   | parenthesized_primary
	'''
	p[0] = p[1]

# Changed grammar from # parenthesized_primary : '(' expression ')'
def p_parenthesized_primary(p):
	'''parenthesized_primary : '(' simple_expression ')'
	'''
	p[0] = p[2]
	
def p_statement_s(p):
	'''statement_s : statement
	   | statement_s M statement
	'''
	p[0] = deepcopy(p[1])
	if (len(p) > 2):
		p[0] = deepcopy(p[3])
		TAC.backpatch(p[1]['next_list'], p[2]['quad'])
	
def p_statement(p):
	'''statement : unlabeled
	'''
	p[0] = p[1]
	
def p_unlabeled(p):
	'''unlabeled : simple_stmt
	   | compound_stmt
	'''
	p[0] = p[1]

def p_simple_stmt(p):
	'''simple_stmt : assign_stmt
	   | return_stmt
	   | procedure_call
	'''
	p[0] = p[1]
	if p[0] == None or not 'next_list' in p[0]:
		p[0] = {'next_list': []}

def p_compound_stmt(p):
	'''compound_stmt : if_stmt
	   | loop_stmt
	   | block
	'''
	p[0] = deepcopy(p[1])
	
# Changed grammar from # assign_stmt : name ASSIGN expression ';'
def p_assign_stmt(p):
	'''assign_stmt : name ASSIGN simple_expression ';'
	'''
	TAC.emit(lhs=p[1]['tag'],op1=p[3],op='ASSIGN')
	# TAC.resetTemp(ST)
	
def p_if_stmt(p):
	'''if_stmt : IF cond_clause_s else_opt END IF ';'
	'''
	p[0] = deepcopy(p[2])
	p[0]['next_list'] = TAC.merge(p[2]['next_list'], p[3]['next_list'])
	TAC.backpatch(p[2]['false_list'], p[3]['quad'])
	
def p_cond_clause_s(p):
	'''cond_clause_s : cond_clause
	   | cond_clause_s ELSIF M cond_clause
	'''
	p[0] = deepcopy(p[1])
	if (len(p) > 2):
		p[0]['next_list'] = TAC.merge(p[1]['next_list'], p[4]['next_list'])
		TAC.backpatch(p[1]['false_list'], p[3]['quad'])
		p[0]['false_list'] = p[4]['false_list']

def p_N (p):
	'''N :
	'''
	p[0] = {'quad': TAC.getLine()}
	TAC.emit(op='goto',lhs=None)

def p_cond_clause(p):
	'''cond_clause : cond_part statement_s N
	'''
	TAC.backpatch(p[1]['false_list'], p[3]['quad'])
	p[0] = deepcopy(p[1])
	p[0]['next_list'] = TAC.merge(p[2]['next_list'],[p[3]['quad']])
	
def p_cond_part(p):
	'''cond_part : condition THEN
	'''
	p[0] = deepcopy(p[1])
	
def p_condition(p):
	'''condition : expression
	'''
	p[0] = p[1]
	
def p_else_opt(p):
	'''else_opt :
	   | ELSE M statement_s
	'''
	p[0] = {'next_list': []}
	if len(p) == 1:
		p[0]['quad'] = TAC.getLine()
	else:
		p[0] = deepcopy(p[3])
		p[0]['quad'] = p[2]['quad']
	
def p_loop_stmt(p):
	'''loop_stmt : iteration basic_loop ';'
	'''

def p_iteration(p):
	'''iteration :
	   | WHILE condition
	'''
	
def p_basic_loop(p):
	'''basic_loop : LOOP statement_s END LOOP
	'''

def p_block(p):
	'''block : block_decl block_body END ';'
	'''
	
def p_block_decl(p):
	'''block_decl :
	   | DECLARE decl_part
	'''
	
def p_block_body(p):
	'''block_body : BEGIN statement_s
	'''

# Changed grammar from return_stmt : RETURN ';' | RETURN expression ';'
def p_return_stmt(p):
	'''return_stmt : RETURN ';'
	   | RETURN simple_expression ';'
	'''

def p_subprog_decl(p):
	'''subprog_decl : subprog_spec ';'
	'''
	p[0] = deepcopy(p[1])

# functions to be handled	
# grammar of procedure changed # compound name to def_id
def p_subprog_spec(p):
	'''subprog_spec : PROCEDURE def_id formal_part_opt
	   | FUNCTION def_id formal_part_opt RETURN name
	   | FUNCTION def_id
	'''
	if (len(p) == 4):
		proc_name = p[2]
		attr_dict = {'tag': proc_name, 'param_dict': p[3], 'what': 'procedure'}
		ST.insert(proc_name, attr_dict)
		p[0] = ST.getAttrDict(proc_name)
	
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
		p[0] = dict(p[1].items() + p[3].items())

# need to add this to new symbol table
def p_param(p):
	'''param : def_id_s ':' mark
	'''
	p[0] = {}
	for id in def_id_s:
		dtype = p[3]['tag']
		attr_dict = {'tag': id, 'what': 'var', 'type': dtype}
		p[0][id] = attr_dict

def p_subprog_spec_is_push(p):
	'''subprog_spec_is_push : subprog_spec IS
	'''
	
def p_subprog_body(p):
	'''subprog_body : subprog_spec_is_push decl_part block_body END ';'
	'''
	
def p_procedure_call(p):
	'''procedure_call : name ';'
	'''
	
def p_use_clause(p):
	'''use_clause : USE name_s ';'
	   | USE TYPE name_s ';'
	'''
	
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