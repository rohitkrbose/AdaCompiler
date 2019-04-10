import sys, re, os, logging
from ply import lex, yacc

from Tokens import *
from grammar import *

prog_name = sys.argv[1]
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