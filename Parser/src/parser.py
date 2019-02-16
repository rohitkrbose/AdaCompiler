import sys, re, os, logging
from ply import lex, yacc
from graphviz import Digraph

from Tokens import *
from grammar import *
import grammar as G

dot = Digraph(comment='Abstract Syntax Tree')
special_ = ['c_name_list','compound_name','name_s', 'name', 'id_opt', 'def_id_s']

def DFS (u):
	u.visited = True
	if (u.typ in special_):
		return
	for v in u.children:
		if(str(v.desig)==''):
			if(len(v.children)==0 and v.typ[-3:]=='opt'):
				continue
			else:	
				dot.node(hex(id(v)),v.typ)
				dot.edge(hex(id(u)),hex(id(v)))
		else:
			dot.node(hex(id(v)),str(v.desig))
			dot.edge(hex(id(u)),hex(id(v)))
		DFS(v)
				


def p_error(p):
	print ('line :',p.lineno,'-parser has a problem at token:',p.type)
	parser.errok()

prog_name = sys.argv[1]
out_file_name = sys.argv[2][6:]
with open(prog_name) as fp:
	code = fp.read()
	code = re.sub(re.compile("--.*?\n" ) ,"" ,code) 
	
log_file_name = 'parselog.txt'
logging.basicConfig(level = logging.INFO, filename = log_file_name, filemode = 'w')
log = logging.getLogger()

lexer = lex.lex() # initialize lexer
parser = yacc.yacc(start = 'goal_symbol', debug = True, debuglog=log) # initialize parser
lexer.input(code)

result = parser.parse(code, debug = log)

ast_root = G.root
dot.node(hex(id(ast_root)),str(ast_root.desig))
DFS(ast_root)
dot.render(out_file_name, view=True)  