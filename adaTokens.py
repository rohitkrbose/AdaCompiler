# http://en.wikibooks.org/wiki/Ada_Programming/Lexical_elements
# https://en.wikibooks.org/wiki/Ada_Programming/Delimiters

from reserved_Tokens import *

error_list = []

tokens = [
    'IDENTIFIER',
    'INT',
    'FLOAT',
    'STRING',
    'CHAR',
    'ARROW',
    'DOTDOT',
    'STARSTAR',
    'ASSIGN',
    'NEQ',
    'GEQ',
    'LEQ',
    'LL',
    'RR',
    'BOX',
    'COMMENT',
    'TICK'
] + list(reserved.values())

t_ARROW = r'=>'
t_DOTDOT = r'\.\.'
t_STARSTAR = r'\*\*'
t_ASSIGN = r':='
t_NEQ = r'/=' 
t_GEQ = r'>='
t_LEQ = r'<='
t_LL = r'<<'
t_RR = r'>>'
t_BOX = r'<>'
t_TICK = r'\''

def t_IDENTIFIER(t):
    r'[A-Za-z](_?[A-Za-z0-9])*'
    t.type = reserved.get(t.value.lower(),'IDENTIFIER')
    return t

def t_CHAR(t):
    r'\'.\'' 
    return t

def t_STRING(t):
    r'\"((\"\")|[^"])*\"'
    return t

def t_FLOAT(t):
    r'[+-]?(\d+\.(\d*)?|\.\d+)([eE][+-]?\d+)?'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'[-+]?\d+'
    t.value = int(float(t.value))
    return t

literals = "&()*+,-./:;<=>"

t_ignore  = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'--.*'
    return t

def t_error(t):
    error_list.append("Line:" + str(t.lineno) + " illegal character '%s' found"% t.value[0])
    t.lexer.skip(1)

