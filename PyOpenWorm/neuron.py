"""
.. class:: Neuron

   neuron client
   =============

   This module contains the class that defines the neuron

"""

import sqlite3
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS
from rdflib import URIRef, BNode, Literal
import urllib2
import networkx as nx
import csv

class Neuron:

	def __init__(self, name):
		
		self._name = name
		self.networkX = ''
		self.semantic_net = ''
			
	def _init_networkX(self):
		self.networkX = nx.DiGraph()
		
		# Neuron table
		csvfile = urllib2.urlopen('https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv')
		
		reader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in reader:
			neurontype = ""
			# Detects neuron function
			if "sensory" in row[1].lower():
				neurontype += "sensory"
			if "motor" in row[1].lower():
				neurontype += "motor"    
			if "interneuron" in row[1].lower():
				neurontype += "interneuron"
			if len(neurontype) == 0:
				neurontype = "unknown"
				
			if len(row[0]) > 0: # Only saves valid neuron names
				self.networkX.add_node(row[0], ntype = neurontype)
		
		# Connectome table
		csvfile = urllib2.urlopen('https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv')
		
		reader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in reader:
			self.networkX.add_edge(row[0], row[1], weight = row[3])
			self.networkX[row[0]][row[1]]['synapse'] = row[2]
			self.networkX[row[0]][row[1]]['neurotransmitter'] = row[4]
		
	def _init_semantic_net(self):
		conn = sqlite3.connect('db/celegans.db')
	   
		cur = conn.cursor()
	
		#first step, grab all entities and add them to the graph
	
		cur.execute("SELECT DISTINCT ID, Entity FROM tblentity")
	
		n = Namespace("http://openworm.org/entities/")
	
		# print cur.description
	
		g = Graph()
	
		for r in cur.fetchall():
			#first item is a number -- needs to be converted to a string
			first = str(r[0])
			#second item is text 
			second = str(r[1])
		
			# This is the backbone of any RDF graph.  The unique
			# ID for each entity is encoded as a URI and every other piece of 
			# knowledge about that entity is connected via triples to that URI
			# In this case, we connect the common name of that entity to the 
			# root URI via the RDFS label property.
			g.add( (n[first], RDFS.label, Literal(second)) )
	
	
		#second step, get the relationships between them and add them to the graph
		cur.execute("SELECT DISTINCT EnID1, Relation, EnID2 FROM tblrelationship")
	
		for r in cur.fetchall():
			#print r
			#all items are numbers -- need to be converted to a string
			first = str(r[0])
			second = str(r[1])
			third = str(r[2])
		
			g.add( (n[first], n[second], n[third]) )
	
		cur.close()
		conn.close()
	
		self.semantic_net = g

		
	def GJ_degree(self):
		"""Get the degree of this neuron for gap junction edges only
		
		:returns: total number of incoming and outgoing gap junctions
		:rtype: int
		"""
		if (self.networkX == ''):
			self._init_networkX()
		
		count = 0
		for item in self.networkX.in_edges_iter(self.name(),data=True):
			if 'GapJunction' in item[2]['synapse']:
				count = count + 1
		for item in self.networkX.out_edges_iter(self.name(),data=True):
			if 'GapJunction' in item[2]['synapse']:
				count = count + 1
		return count
	
	
	def Syn_degree(self):
		"""Get the degree of a this neuron for chemical synapse edges only
		
		:returns: total number of incoming and outgoing chemical synapses
		:rtype: int
		"""
		if (self.networkX == ''):
			self._init_networkX()
		count = 0
		for item in self.networkX.in_edges_iter(self.name(),data=True):
			if 'Send' in item[2]['synapse']:
				count = count + 1
		for item in self.networkX.out_edges_iter(self.name(),data=True):
			if 'Send' in item[2]['synapse']:
				count = count + 1
		return count
		
	def type_semantic(self):
		"""Get type of this neuron (motor, interneuron, sensory)
		
		Use the semantic database as the source
			
		:returns: the type
		:rtype: str
		"""
		if (self.semantic_net == ''):
			self._init_semantic_net()
	
		qres = self.semantic_net.query(
		  """SELECT ?objLabel     #we want to get out the labels associated with the objects
		   WHERE {
			  ?node ?p '"""+self.name()+"""' .   #we are looking first for the node that is the anchor of all information about the specified neuron
			  ?node <http://openworm.org/entities/1515> ?object .# having identified that node, here we match an object associated with the node via the 'is a' property (number 1515)
			  ?object rdfs:label ?objLabel  #for the object, look up their plain text label.
			}""")       
	
		type = ''
		for r in qres.result:
			type = str(r[0])
		
		return type
		
	def type_networkX(self):
		"""Get type of this neuron (motor, interneuron, sensory)
		
		Use the networkX representation as the source
			
		:returns: the type
		:rtype: str
		"""
		if (self.networkX == ''):
			self._init_networkX()
		return self.networkX.node[self.name()]['ntype']		

	def type(self):
		"""Get type of this neuron (motor, interneuron, sensory)
			
		:returns: the type
		:rtype: str
		"""
		return self.type_networkX().lower()
		
	def name(self):
		"""Get name of this neuron (e.g. AVAL)
			
		:returns: the name
		:rtype: str
		"""
		return self._name
	
	def receptors(self):
		"""Get receptors associated with this neuron
			
		:returns: a list of all known receptors
		:rtype: list
		"""
		if (self.semantic_net == ''):
			self._init_semantic_net()
	
		qres = self.semantic_net.query(
		  """SELECT ?objLabel     #we want to get out the labels associated with the objects
		   WHERE {
			  ?node ?p '"""+self.name()+"""' .   #we are looking first for the node that is the anchor of all information about the specified neuron
			  ?node <http://openworm.org/entities/361> ?object .# having identified that node, here we match an object associated with the node via the 'receptor' property (number 361)
			  ?object rdfs:label ?objLabel  #for the object, look up their plain text label.
			}""")       
	
		receptors = []
		for r in qres.result:
			receptors.append(str(r[0]))
			
		return receptors
		
	def get_reference(self, type, item=''):
		"""Get a reference back that provides the evidence that this neuron is
		   associated with the item requested as a digital object identifier URL.
		   
		   Example::
		   
		       >>>aval = PyOpenWorm.Neuron('AVAL')
		       >>>aval.receptors()
 			   ['GLR-1', 'NMR-1', 'GLR-4', 'GLR-2', 'GGR-3', 'UNC-8', 'GLR-5', 'NMR-2']
 			   #look up what reference says this neuron has a receptor GLR-1
		       >>>aval.get_reference(0,'GLR-1')
		       http://dx.doi.org/10.100.123/natneuro
		       #look up what reference says this neuron has a neighbor DD5
		       >>>aval.get_reference(1, 'DD5')
		       http://dx.doi.org/20.140.521/ploscompbiol
		   
		   :param type: The kind of thing to search for.  Valid options are: 0=receptor, 1=neighbor 
		   :param item: Name of the item requested, if appropriate
		   :returns: a Digital Object Identifier (DOI) as a URL
		   :rtype: URL
		   """
		   
	def get_neighbors(self, type=0):
		"""Get a list of neighboring neurons.  
		
		   :param type: What kind of junction to look for.  
		                0=all, 1=gap junctions only, 2=all chemical synapses
		                3=incoming chemical synapses, 4=outgoing chemical synapses
		   :returns: a list of neuron names
		   :rtype: List
		   """
	
	
	# This method can start out life by reading in the nml files
	# from GitHub
	#def as_neuroml(self):
	#   """Return this neuron as a NeuroML representation
	#	:rtype: str
	#   """
	
	#def rdf(self):
	
	
	
	#def peptides(self):
	
	