class ActivationRecord:

	def __init__ (self):
		self.neg_offset = 0
		self.pos_offset = 8
		self.act_rec = {'return_addr': 8}

	def insert_local (self, var, attr_dict):
		if attr_dict['what'] == 'var':
			width = 4 if attr_dict['type'] == 'Integer' else 8
			self.neg_offset += width
			self.act_rec[var] = -self.neg_offset
		elif attr_dict['what'] == 'array':
			width = 4 if attr_dict['type'] == 'Integer' else 8
			size = attr_dict['r_end_s'] - attr_dict['r_start_s'] + 1
			self.neg_offset += width*size
			self.act_rec[var] = -self.neg_offset
		elif attr_dict['what'] == 'record_type':
			for k,v in attr_dict.items():
				if k not in ['what','tag']:
					rec_ele = var + '.' + v['tag']
					width = 4 if v['type'] == 'Integer' else 8
					self.neg_offset += width
					self.act_rec[rec_ele] = -self.neg_offset

	def insert_param (self, var, attr_dict):
		if attr_dict['what'] == 'var':
			width = 4 if attr_dict['type'] == 'Integer' else 8
			self.pos_offset += width
			self.act_rec[var] = self.pos_offset
		elif attr_dict['what'] == 'record_type':
			for k,v in attr_dict.items():
				if k not in ['what','tag']:
					rec_ele = var + '.' + v['tag']
					width = 4 if v['type'] == 'Integer' else 8
					self.pos_offset += width
					self.act_rec[rec_ele] = self.pos_offset