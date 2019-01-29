import sys,lex,re
from adaTokens import *
from colour import *

cfg_file = sys.argv[1][6:]
prog_name = sys.argv[2]
output_file = sys.argv[3][9:]
enc = createColDict(cfg_file)

lexer = lex.lex()
with open(prog_name) as fp:
    data = fp.read() + '\n'
    lexer.input(data)
    datalist = data.split('\n')
    actstring = []
    tokstring = ''
    old_line = lexer.lineno
    H = '<!DOCTYPE html><html><head><title>'+prog_name+'</title></head><body>'

    for tok in lexer:
        if(tok.lineno != old_line) :
            tokstring = tokstring.strip()
            h = getHTML(actstring,tokstring.split(' '),enc)
            H += h
            actstring = []
            tokstring = ''
            old_line = tok.lineno
        actstring.append(tok.value)
        tokstring += ' ' + str(tok.type)
    
    tokstring = tokstring.strip()
    h = getHTML(actstring,tokstring.split(' '),enc)
    H += h
    H += '</body></html>'
    with open(output_file, "w") as out:
        out.write(H)

if error_list : 
    print  ("=====ERRORS=====")
    print ('\n'.join(error_list), )