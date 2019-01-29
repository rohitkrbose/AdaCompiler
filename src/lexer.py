import sys,re
from ply import lex
from Tokens import *
from Colour import *

cfg_file = sys.argv[1][6:] # Config file
prog_name = sys.argv[2] # Code file
output_file = sys.argv[3][9:] # Output HTML file

enc = createColDict(cfg_file) # Get keyword-to-colour mapping

H = '<!DOCTYPE html><html><head><title>'+prog_name+'</title></head><body>' # HTML document output

with open(prog_name) as fp:
    code = fp.read() + '\n'

lexer = lex.lex() # Initialize lexer
lexer.input(code)
actstring = [] # Actual lexemes
tokenstring = [] # Token types
c_line = lexer.lineno

for token in lexer:
    if(token.lineno != c_line) : # once we get to next line
        H += getHTML(actstring,tokenstring,enc) # get colour-formatted HTML code for current line
        actstring = []
        tokenstring = []
        c_line = token.lineno # update current line number
    actstring.append(token.value)
    tokenstring.append(str(token.type))

H += getHTML(actstring,tokenstring,enc) # get colour-formatted HTML code for current line

H += '</body></html>'
with open(output_file, 'w') as fp: # Write to HTML file
    fp.write(H)

# Print errors on terminal
if (len(errors) > 0): 
    print  ("--------ISSUES--------")
    for e in errors:
        print (e)