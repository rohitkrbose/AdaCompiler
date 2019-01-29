# This file loads colour scheme config file and generates HTML code accordingly

# create dictionary that maps keyword type to colour
def createColDict (file_name):
	D = {}
	with open(file_name) as fp:
		toklist = fp.read().split('\n')
		for tok in toklist:
			ind = tok.find(',')
			name = tok[:ind]
			colour = tok[ind+1:]
			D[name] = colour
	return (D)

def getHTML(actual,token,D):
	Z = '' # final HTML code string to be returned
	for i in range (len(actual)):
		s = '<font color=' # format HTML code
		if (token[i] in D.keys()):
			s += D[token[i]]
		elif (token[i][-5:] == '_TYPE'): # data_type
			s += D['_TYPE']
		elif (token[i] in '&()*+,-./:;<=>'): # simple literal
			s += D['LITERALS']
		else:
			s += D['DEFAULT']
		s += '>' + str(actual[i]) + ' &nbsp;</font>' # format HTML code
		Z += s
	Z += '</br>' # newline
	return (Z)