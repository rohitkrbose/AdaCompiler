import sys,re
from ply import lex
from Tokens import *
from Colour import *

cfg_file = sys.argv[1][6:]
prog_name = sys.argv[2]
output_file = sys.argv[3][9:]
enc = createColDict(cfg_file)
H = '<!DOCTYPE html><html><head><title>'+prog_name+'</title></head><body>'

lexer = lex.lex()
with open(prog_name) as fp:
    code = fp.read() + '\n'
    lexer.input(code)
    actstring = []
    tokenstring = []
    c_line = lexer.lineno

    for token in lexer:
        if(token.lineno != c_line) :
            H += getHTML(actstring,tokenstring,enc)
            actstring = []
            tokenstring = []
            c_line = token.lineno
        actstring.append(token.value)
        tokenstring.append(str(token.type))
    
    H += getHTML(actstring,tokenstring,enc)

H += '</body></html>'
with open(output_file, 'w') as fp:
    fp.write(H)

if (len(errors) > 0): 
    print  ("--------ISSUES--------")
    for e in errors:
        print (e)