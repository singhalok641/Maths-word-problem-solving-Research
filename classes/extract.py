'''
Class to extract direct information for the question
'''
from classes import *

class Extract_direct(graph.Graph,parsers.Parser):

	def __init__(self,question,parse):
		self.question=question
		self.parse=parse
		self.node_list=[]
		super(Extract_direct, self).__init__()
		self.quantity=0
		self.word_dic={}
		self.li=[]
		self.numeric_li=[]

	def distingush_word(self):
		ques=self.question
		for word in self.parse:
			if(word.dep_=="nummod"):
				qword=word.head.text
				cword=lemmatizer.lemmatize(word.head.text)
				try:
					match = next(val for key, val in self.word_dic.items() if cword in key)
					self.word_dic[cword]=self.word_dic[cword]+1
					#print(self.word_dic[cword])
				except StopIteration:
					self.word_dic[cword]=1
				fword=cword+str(self.word_dic[cword])
				print(fword)
				qword=qword+' '
				fword=fword+' '
				new_question=str.replace(self.question,qword,fword, 1)
				print(new_question)
				self.question=new_question
		self.parse=super(Extract_direct,self).dependency_parsing(self.question)
		print(self.question)
		return self.question

	def node(self):
		'''Adds nodes and specifies its head
		'''
		for word in self.parse:
			#print(word.text,word.head.text,word.dep_,word.pos_)
			if word.pos_=="NUM" or word.pos_=="NOUN" or word.pos_=="PROPN"or word.pos_=="VERB":
				if word.dep_=="nummod":
					#self.quantity=self.quantity+1
					cword=word.head.text
					#cword=lemmatizer.lemmatize(word.head.text)
					#if cword not in self.node_list:
					#	self.node_list.append(cword)
					#cword1=cword+str(self.quantity)
					self.add_numeric(word.text,cword)
				elif word.text not in stop and word.text not in self.node_list:	
					w=lemmatizer.lemmatize(word.text)
					self.node_attr(w,word.pos_)

	def node_attr(self,word,word_pos):
		'''add head attribute of the node
		
		Arguments:
			word {[the name of the node]} 
			word_pos {[poas tag of the word]}
		'''
		if word_pos=="VERB":	
			super(Extract_direct,self).add_node_attr(word,"Head","Function")
			self.node_list.append(word)
		elif word_pos=="NOUN" or word_pos=="PROPN":
			self.node_list.append(word)
			super(Extract_direct,self).add_node_attr(word,"Head","Entity")

	def add_numeric(self,number,container):
		'''Function that makes nodes and defined their head
		
		Takes nodes (only nummod relations and adds their properties) 
		
		Arguments:
			number {[numeric dependent quantity]}
			container {[head of nummod relation]}
		'''
		print("added")
		self.node_list.append(container)
		super(Extract_direct,self).add_node_attr(number,"Head","Quantity")
		super(Extract_direct,self).add_node_attr(container,"Head","Container")
		super(Extract_direct,self).att_edge(container,number,"Relation","Quantity")


	def add_edges(self):
		'''Adds edges between adges
		searches in list of nodes and if there is a dependency add a node
		
		Arguments:
			list_nodes {[list]} -- [list of nodes]
			dep {[object]} -- [spacy parser result]
		'''
		lemmatizer = WordNetLemmatizer()
		for word in self.parse:
			a=lemmatizer.lemmatize(word.text)
			b=lemmatizer.lemmatize(word.head.text)
			if (a in self.node_list and b in self.node_list):
				self.add_egde_attr(a,b,word.dep_)
				#if(self.check_connectivity(a,b)):
					#print(word.text,word.head.text)
		
	def add_egde_attr(self,word,head,dep):
		#if(dep=="nummod"):
		#	print("Adding edge between container and quantity")
		#	super(Extract_direct,self).att_edge(head,word,"Relation","Quantity")	
		#print("Adding edge between container and property")
		super(Extract_direct,self).att_edge(head,word,"Relation","Property")

	def check_connectivity(self,node1,node2):
		if(super(Extract_direct,self).return_node_head(node1)=="Container" and super(Extract_direct,self).return_node_head(node2)["Head"]=="Container"):
			return False
		else:
			return True

	def name_nodes(self,node_list,dep_parse):
		for word in dep_parse:
			if(word.dep_=="nummod"):
				#print(word.text,word.head.text)
				super(Extract_direct,self).add_att()

	def sen_tok(self):
		sent_tokenize_list = sent_tokenize(self.question)
		return sent_tokenize_list

	def numeric_dep(self):
		for word in self.parse:
			print(word.head.text,word.text,word.dep_)
		for word in self.parse:
			#print(word.head.text,word.text,word.dep_)
			if(word.pos_=="NUM"):
				self.li.append(self.position(word))
				#print("Printing numeric relations")
				self.add_name_node(word)
				for child in word.children:
					if self.check_pos(child) and self.remove_stopwords(child):
						self.add_name_node(child)
						super(Extract_direct,self).add_edge(self.position(str(word.text)),self.position(str(child)))	
						self.li.append(self.position(child))
						self.recurse(child,word)
					else:
						self.li.append(self.position(child))
						self.recurse(child,word)
				for ans in word.ancestors:
					if self.check_pos(ans) and self.remove_stopwords(ans):
						self.add_name_node(ans)
						super(Extract_direct,self).add_edge(self.position(str(word.text)),self.position(str(ans)))	
						self.li.append(self.position(ans))
						self.recurse(ans,word)
					else:
						self.li.append(self.position(ans))
						self.recurse(ans,word)
	
	def recurse(self,ite_word,prev_word):
		#print("main word"+str(ite_word))
		#print("Printing nodes"+str(self.numeric_li))
		print("Printig in recurse"+str(ite_word.text),str(prev_word))	
		for word in self.parse:
			if (str(word.text) == str(ite_word)):
				for child in word.children:
					#print("Children is "+ str(child),str(self.li))
					if self.position(child) not in self.li and self.check_pos(child) :
						self.add_name_node(child)
						if self.check_pos(word) :
							self.add_name_node(word)
							prev_word=child
							super(Extract_direct,self).add_edge(self.position(str(word.text)),self.position(str(child)))	
							#self.li.append(self.position(child))				
							self.recurse(child,prev_word)
					elif self.position(child) not in self.li and self.check_pos(word) :
						print("in ahlf half"+str(prev_word.text),str(word.text))
						super(Extract_direct,self).add_edge(self.position(str(word.text)),self.position(prev_word))
						prev_word=word
						#self.li.append(self.position(child))				
						self.recurse(child,prev_word)
					elif self.position(child) not in self.li:
						#self.li.append(self.position(child))
						self.recurse(child,prev_word)
				for ans in word.ancestors:
					#print("Anscester is "+str(ans),str(self.li))
					if self.position(ans) not in self.li and self.check_pos(ans) :
						#print("goes into"+str(ans))
						self.add_name_node(ans)
						if self.check_pos(word) :
							self.add_name_node(word)
							prev_word=ans
							super(Extract_direct,self).add_edge(self.position(str(word.text)),self.position(str(ans)))	
							self.li.append(self.position(ans))
							self.recurse(ans,prev_word)
					elif self.position(ans) not in self.li and self.check_pos(word):
						print("in ans half"+str(prev_word.text),str(word.text))
						super(Extract_direct,self).add_edge(self.position(str(word.text)),self.position(prev_word))
						prev_word=word
						self.li.append(self.position(ans))				
						self.recurse(ans,prev_word)
					elif self.position(ans) not in self.li:
						self.li.append(self.position(ans))				
						self.recurse(ans,prev_word)


	def position(self,child):
		y=self.question.find(str(child))
		#print(str(child) +' '+str(y))
		return y

	def add_name_node(self,child):
		a=self.position(child)
		self.numeric_li.append(child)
		super(Extract_direct,self).add_node_attr(a,"name",child)

	def check_pos(self,ans):
		if (ans.pos_=="NOUN" or ans.pos_=="PROPN" or ans.pos_=="VERB" or ans.pos_=="NUM" or ans.pos_=="ADJ"):
			return True
		else:
			return False

	def remove_stopwords(self,word):
		if word.text.lower() not in stop:
			return True
		else:
			return False