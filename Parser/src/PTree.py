def wordRep(w) :
	D = { '&': 'ampersand',
	'(': 'open_bracket',
	')': 'close_bracket',
	'*': 'star',
	'+': 'plus',
	',': 'comma',
	'-': 'hyphen',
	'.': 'dot',
	'/': 'forward_slash',
	':': 'colon',
	';': 'semi_colon',
	'<': 'less',
	'=': 'equal',
	'>': 'more',
    '<empty>' : 'empty',
	}
	return (D.get(w,w))


def constructTree(file_name, log_file_name) :
	dot_file = open(file_name.split('.')[0] + '.dot', 'w')
	log_file = open(log_file_name, 'r')
	U = {'goal_symbol':{'List':[0] , 'count':1}}
	imp_info = []

	for line in reversed(log_file.readlines()):
		if (line.find('INFO:root:Action : Reduce rule') != -1):
			imp_info.append(line.split('[')[1].split(']')[0])

	# Write dot code to dot_file to generate graph
	dot_file.write('digraph Parse_tree {\n')
	for line in imp_info:
		L = line.split('->')[0].replace(' ','')
		R = line.split('->')[1].split(' ')
		L_token =  wordRep(L) +  str(U[L]['List'][-1])
		del U[L]['List'][-1]
		dot_file.write('\t' + L_token + '[ label =' + '\"' + L  + '\"''];\n')
		for R_word in R:
			if (R_word != ''):
				if R_word not in U : 
					U[R_word] = {'List':[0] , 'count':1}
					R_token = wordRep(R_word) + '0'
				else: 
					count = int(U[R_word]['count']) 
					U[R_word]['List'].append(count)
					R_token =  wordRep(R_word) + str(count)
					U[R_word]['count'] = count + 1
				dot_file.write('\t' + R_token + '[ label =' + '\"' + R_word  + '\"''];\n')
				dot_file.write('\t' + L_token  + '->' + R_token + ';\n')
	dot_file.write('}\n')

	dot_file.close()
	log_file.close()