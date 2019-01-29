def createColDict (file_name):
	D = {}
	with open(file_name) as fp:
		toklist = fp.read().split('\n')
		for tok in toklist:
			ind = tok.find(',')
			name = tok[:ind]
			col = tok[ind+1:]
			D[name] = col
	return (D)

def getHTML(actual,token,D):
	n = len(actual)
	Z = ''
	for i in range (n):
		s = '<font color='
		if (token[i] in D.keys()):
			s += D[token[i]]
		elif (token[i][-5:] == '_TYPE'):
			s += D['_TYPE']
		elif (token[i] in '&()*+,-./:;<=>'):
			s += D['LITERALS']
		else:
			s += D['DEFAULT']
		s += '>' + str(actual[i]) + ' &nbsp;</font>'
		Z += s
	Z += '</br>'
	return (Z)