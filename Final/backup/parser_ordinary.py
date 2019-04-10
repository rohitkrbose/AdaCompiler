import sys, re, os, logging
from ply import lex, yacc

from Tokens import *
import PTree
from grammar import *
import grammar as G


special_ = ['c_name_list','compound_name','name_s', 'name', 'id_opt', 'def_id_s', 'value_s']

def DFS (u):
	u.visited = True
	print (u.typ, '|', u.desig)
	if (u.typ in special_):
		return
	for v in u.children:
		if (v.visited == False):
			DFS(v)

prog_name = sys.argv[1]
with open(prog_name) as fp:
	code = fp.read()

log_file_name = 'parselog.txt'
logging.basicConfig(level = logging.INFO, filename = log_file_name, filemode = 'w')
log = logging.getLogger()

lexer = lex.lex() # initialize lexer
parser = yacc.yacc(start = 'goal_symbol', debug = True, debuglog=log) # initialize parser
lexer.input(code)

result = parser.parse(code, debug = log)

PTree.constructTree(prog_name, log_file_name)

ast_root = G.root
DFS(ast_root)