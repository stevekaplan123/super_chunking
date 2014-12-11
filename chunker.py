class Rule:
	from nltk.tree import Tree
	def __init__(self, contents, type):
		self.contents = contents
		self.type = type
###################################################
	def rule_to_children(self, tree, children):
		#create a string, total, based on contents of children values (different whether subtree or leaf)
		current = ""
		total=""
		ruleContents = self.contents

		for child in children:
			if type(tree[child]) is Tree: 			 #subtree
				current = tree[child].node
			elif type(tree[child]) is tuple: 		#leaf with special info
				current = tree[child][-1]	 #-1 gets us POS tag 
			else:						#leaf without any special info
				current = tree[child]
		
			total+=current+" "
	

		#now see if total is governed by rule, and if so, where and how many times
		#list_positions is a list of tuple values of the start and end positions
		#of the rule being instantiated by string total
	
		import re
		pattern = re.compile(ruleContents)
		list_pattern = re.split(pattern, total)
		tuple_position = ()
		len_rule = len(ruleContents.split())

		if len(list_pattern)>1:
			start = len(list_pattern[0].split())
			tuple_position = (start, start+len_rule)
		else:
			tuple_position = (-1,-1)
	
		return tuple_position
####################################################		
	def find_brothers(self, children, parent):
		#find_brothers creates a dictionary where the key is the parent/root
		#and the value is the list of its children, who are "brothers"
		allBrothers = []
		tempBrothers = []
		dictBrothers = {} #key -> parent; value -> list of children

		#set up parental info for each child of tree
		#so that: parent[child] = child's parent
		if () in children:
			children.remove(()) #remove () since we do not need root as it has no parents or brothers
		for child in children:
			parent[child] = child[0:-1] #parent info is everything in
					#tuple except last value in 
					#treepositions() tuples
	
		for child in children:
	   	  if not child in allBrothers: #ensures no redundancy in dictBrothers
		   	tempBrothers = []
	           	allBrothers.append(child) #all children already considered
		   	tempBrothers.append(child) 
		   	for otherChild in children:
				if not otherChild in allBrothers:
			  	  if parent[otherChild]==parent[child]:
					tempBrothers.append(otherChild)
					allBrothers.append(otherChild)

		  	if len(tempBrothers) > 1:
				dictBrothers[parent[child]] = tempBrothers

		return dictBrothers
##########################################################
	def chunk(self, tree, rule, depth):

		ruleContents = rule.contents
		ruleName = rule.type

		if depth==0:  #maximum recursion set by depth
			return tree
	
		children = tree.treepositions('postorder') #get tuples for all locations in tree
	
		string = ""
		parent = {}
		subtrees = {} #key->new subtree to add to tree; value->location to place in treepositions()


		dictBrothers = rule.find_brothers(children, parent) # returns a dict. of those children in the tree who have the same parent, 
							# such that a rule MIGHT apply to them	

		if dictBrothers == dict(): # no possible application of rule
			return tree

		#now we have dictBrothers which is a list of all children who have the same parent,
		#we check to see which list of brothers corresponds to ruleContents
		#such that tree will need to be altered at that location

		for child in children:
			# look for a child in tree for whom it both (1) has brothers and (2) rule applies (rule_to_children(tree, brothers, rule))
			 # otherwise, just "continue"
	    		if not parent[child] in dictBrothers: 
				continue
			tempBrothers = dictBrothers[parent[child]]
			tuple = self.rule_to_children(tree, tempBrothers)
			if tuple == (-1,-1):
				continue
		
			#found a rule applies for certain children
			#now set up new tree
			#and re-arrange tree to fit
			#then recursively call chunker with depth-1

		
			start = tuple[0]
			end = tuple[1]

			newTree = Tree("("+ruleName+")")
		
			for i in range(end-start):  				#set up new tree
	
				newChild = tempBrothers[i+start]
				
				ruleList = ruleContents.split()	
			
			
				typeOf = type(tree[newChild])
				if typeOf is Tree:
					modifiedName = "<"+tree[newChild].node+">"			 
					tree[newChild].node = modifiedName
				else:
					#ruleList = ruleContents.split()	
					#subst="-->"
					#for i in range(len(rule)):
						#subst+="<"+ruleList[i]+"> " 		#add this so we know how tree was derived
					newTuple = (tree[newChild][0], "<"+str(tree[newChild][-1])+">")
					tree[newChild] = newTuple
	

				newTree.append(tree[newChild]) 		
		
			tree[tempBrothers[start]] = newTree 	#attach new tree at left-most child (start)
								#then remove old children except for 
								#0/start, which is the new tree
		
			for i in range(end-start):		
		 	  if i != 0:		
				tree[tempBrothers[i+start]] = "REMOVE"
		
			while "REMOVE" in tree:
				tree.remove("REMOVE")

			for subtree in tree.subtrees():
				if "REMOVE" in subtree:
					subtree.remove("REMOVE")

				
			#now recursively chunk if there are more brothers
			#to whom rule applies
			if len(dictBrothers)>1 or len(dictBrothers[parent[child]])>len(ruleContents.split()):
				return self.chunk(tree, rule, depth-1)
			else:		    
				return tree

		#found no children for whom rule applies, so just return tree
		return tree


########END OF RULE CLASS#################
###########################################
from nltk.tree import Tree
from nltk.corpus import treebank_chunk
def printTree(tree, file, tabs=0):
	file.write('\n')
	for i in range(tabs):
		file.write('\t')
	file.write("("+tree.node)
	for node in tree:
		if type(node) is Tree:
			printTree(node, file, tabs+1)
		else:
			for i in range(tabs+1):
				file.write('\t')
			file.write("(")
			file.write(str(node[0]))
			file.write(" ")
			file.write(str(node[1]))
			file.write(")")
	for i in range(tabs+1):
		file.write('\t')
	file.write(')\n')

#########################################
def main():
	files = ["wsj_0156.pos",
		"wsj_0160.pos",
		"wsj_0163.pos",
		"wsj_0165.pos",
		"wsj_0167.pos",
		"wsj_0170.pos",
		"wsj_0175.pos",
		"wsj_0187.pos",
		"wsj_0195.pos",
		"wsj_0196.pos"]
	test_trees = treebank_chunk.chunked_sents(files)
	
	NP_rules = ["NP , NP CC NP", "NP CC NP", "NP IN NP", "NP TO NP", "NP NP", "NP NN NP", "NP , NP ,", "RB VBN NP"]
	#NP_rules = ["DT NN", "JJ NN", "DT NP"] #these rules can be tried to show that multiple kinds of chunking work 
	rules = []
	##create rule objects
	for ruleString in NP_rules:
		newRule = Rule(ruleString, "NP")
		rules.append(newRule)

	myChunks = open("superchunks.txt","a")
	for tree in test_trees:
	        for rule in rules:
			tree = rule.chunk(tree, rule, 15)
		printTree(tree, myChunks)

	
#########################################################
