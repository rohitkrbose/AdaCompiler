# http://en.wikibooks.org/wiki/Ada_Programming/Lexical_elements
# https://en.wikibooks.org/wiki/Ada_Programming/Delimiters

from Keywords import *

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
    # 'COMMENT',
    'TICK'
] + list(reserved.values())
errors = []

# Complex literals
t_ARROW = r'=>'
t_DOTDOT = r'\.\.'
t_STARSTAR = r'@@'
t_ASSIGN = r':='
t_NEQ = r'/=' 
t_GEQ = r'>='
t_LEQ = r'<='
t_LL = r'<<'
t_RR = r'>>'
t_BOX = r'<>'
t_TICK = r'\''

literals = "&()*+,-./:;<=>" # Simple literals

def t_IDENTIFIER(t):
    r'[A-Za-z](_?[A-Za-z0-9])*'
    t.type = reserved.get(t.value.lower(),'IDENTIFIER') # If reserved keyword, then it is given priority. Default is identifier!
    return t

def t_CHAR(t):
    r'\'.\''  # Any single character enclosed within single quotes
    return t

def t_STRING(t):
    r'\"((\"\")|[^"])*\"' # Any set of characters enclosed within double quotes"
    return t

def t_FLOAT(t):
    r'[+-]?(\d+\.(\d*)?|\.\d+)([eE][+-]?\d+)?' # Definition of Float
    t.value = float(t.value)
    return t

def t_INT(t):
    r'[-+]?\d+' # Definition of Int
    t.value = int(float(t.value))
    return t

t_ignore  = ' \t' # Ignore spaces and tabs

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value) # Helps counting lines

def t_COMMENT(t):
    r'--.*' # Ada comment
    return t

def t_error(t):
    errors.append('Line:' + str(t.lineno) + 'unusual char \'' + t.value[0] + '\'') # If any weird character is found
    t.lexer.skip(1)