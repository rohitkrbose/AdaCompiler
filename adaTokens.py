# http://en.wikibooks.org/wiki/Ada_Programming/Lexical_elements
# https://en.wikibooks.org/wiki/Ada_Programming/Delimiters

from reserved_Tokens import *

error_list = []

tokens = [
    'IDENTIFIER',
    'INTEGER',
    'FLOAT',
    'STRING',
    'CHAR',
    'ARROW',
    'DOTDOT',
    'STARSTAR',
    'ASSIGNMENT',
    'NOTEQUAL',
    'GREATER',
    'LESS',
    'GREATEREQ',
    'LESSEQ',
    'LLBRACKET',
    'RLBRACKET',
    'BOX',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'AMPERSAND',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'DOT',
    'COLON',
    'SEMICOLON',
    'EQUAL',
    'TICK' #Special Token
] + list(reserved.values())

t_ARROW = r'=>'
t_DOTDOT = r'\.\.'
t_STARSTAR = r'\*\*'
t_ASSIGNMENT = r':='
t_NOTEQUAL = r'/='
t_GREATER = r'\>'
t_LESS = r'\<' 
t_GREATEREQ = r'>='
t_LESSEQ = r'<='
t_LLBRACKET = r'<<'
t_RLBRACKET = r'>>'
t_BOX = r'<>'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_AMPERSAND = r'\&'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r'\,'
t_DOT = r'\.'
t_COLON = r'\:'
t_SEMICOLON = r'\;'
t_EQUAL = r'\='

def t_IDENTIFIER(t):
    r'[A-Za-z](_?[A-Za-z0-9])*'
    t.type = reserved.get(t.value.lower(),'IDENTIFIER')
    return t

def t_CHAR(t):
    r'\'.\'' 
    return t

def t_STRING(t):
    r'(\"([^\\\"]|(\\.))*\")|(\'([^\\\']|(\\.))*\')'
    return t

def t_TICK(t):
    r'\''
    return t

# float and integer not getting recognized separately

def t_FLOAT(t):
    r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
    t.value = float(t.value.replace("_",""))
    return t

def t_INTEGER(t):
    r'[+-]?[0-9](_?[0-9]+)*([Ee](\+)?[0-9](_?[0-9]+)*)?'
    t.value = int(float(t.value.replace("_","")))
    return t

t_ignore  = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'--.*'

def t_error(t):
    error_list.append("Line:" + str( t.lineno) + " illegal character '%s' found"% t.value[0])
    t.lexer.skip(1)

