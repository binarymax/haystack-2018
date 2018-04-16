import re
from graphviz import Digraph

eol = u' ;\n'
eop = u' .\n\n'
head= u'\
@prefix dc:      <http://purl.org/dc/elements/1.1/> .\n\
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .\n\
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .\n\
@prefix dcterms: <http://purl.org/dc/terms/> .\n\n'

def strToUri(term):
	uri = re.sub(r"[^\w\s]", '', term)
	uri = re.sub(r"\s+", '-', uri)
	return uri

def leftPad(num=0,mag=2):
	return u' '*(mag*num)

class Label:
	def __init__(self,label,lang=u'en',isPref=False):
		self.isPref = isPref
		self.label = label
		self.lang = lang
		self.count = 0

	def pref(self):
		self.isPref = True

	def turtle(self):
		text =  u'skos:' + (u'pref' if self.isPref else u'alt') + u'Label '
		text += u'"' + self.label + u'"@' + self.lang
		return text

class Concept:
	def __init__(self,scheme,uri,identifier=None):
		self.scheme = scheme
		self.uri = uri
		self.identifier = identifier
		self.labels = dict()
		self.narrower = []
		self.broader = []
		self.related = []
		self.top = False
		self.count = 0
		self.slop = 1

	def label(self,term,lang=u'en',isPref=False,slop=1):
		self.count+=1
		if term not in self.labels.keys():
			self.labels[term] = Label(term,lang,isPref)
		self.labels[term].count += 1
		if slop>self.slop:
			self.slop = slop

	def identifyTop(self):
		if len(self.broader)==0:
			self.top = True
		else:
			self.top = False

	def prefLabel(self):
		defLabel = None
		for label in self.labels.keys():
			if self.labels[label].isPref:
				return self.labels[label].label
			else:
				defLabel = label
		if defLabel:
			return self.labels[defLabel].label
		return self.identifier

	def turtle(self):
		self.identifyTop()
		text = self.uri + u' a skos:Concept' + eol
		for label in self.labels.keys():
			text += leftPad(1) + self.labels[label].turtle() + eol
		for broad in self.broader:
			text += leftPad(1) + u'skos:broader ' + broad + eol
		for narrow in self.narrower:
			text += leftPad(1) + u'skos:narrower ' + narrow + eol
		for relate in self.related:
			text += leftPad(1) + u'skos:related ' + relate + eol
		text += leftPad(1) + u'skos:inScheme ' + self.scheme + eop
		return text


class ConceptScheme:
	def __init__(self,uri,title,identifier):
		self.uri = uri
		self.title = title
		self.identifier = identifier
		self.concepts = dict()

	def concept(self,uri,identifier):
		if not uri in self.concepts.keys():
			self.concepts[uri] = Concept(self.uri,uri,identifier)
		return self.concepts[uri]

	def narrower(self,broaderUri,narrowerUri):
		broad = self.concepts[broaderUri]
		narrow = self.concepts[narrowerUri]
		if narrowerUri not in broad.narrower:
			broad.narrower.append(narrowerUri)
		if broaderUri not in narrow.broader:
			narrow.broader.append(broaderUri)

	def relate(self,relatedUri1,relatedUri2):
		related1 = self.concepts[relatedUri1]
		related2 = self.concepts[relatedUri2]
		if relatedUri1 not in related2.related:
			related2.related.append(relatedUri1)
		if relatedUri2 not in related1.related:
			related1.related.append(relatedUri2)

	def turtle(self):
		text = self.uri + u' a skos:ConceptScheme' + eol
		text += leftPad(1) + u'skos:prefLabel "' + self.title + u'"@en' + eol
		text += leftPad(1) + u'dcterms:title "' + self.title + u'"@en' + eol
		text += leftPad(1) + u'dcterms:identifier "' + self.identifier + u'"@en' + eop
		for concept in self.concepts.keys():
			text += self.concepts[concept].turtle()
		return text

	def dot(self,engine,format):
		D = Digraph(self.title,format=format,engine=engine)
		D.node(self.identifier,self.title)
		for uri in self.concepts.keys():
			concept = self.concepts[uri]
			D.node(concept.identifier,concept.prefLabel())
		for uri in self.concepts.keys():
			concept = self.concepts[uri]
			if len(concept.broader)==0:
				D.edge(self.identifier,concept.identifier)
			for narrower in concept.narrower:
				D.edge(concept.identifier,self.concepts[narrower].identifier)
		return D


class SKOS:
	def __init__(self):
		self.schemes = dict()

	def scheme(self,uri,title,identifier):
		if not uri in self.schemes.keys():
			self.schemes[uri] = ConceptScheme(uri,title,identifier)
		return self.schemes[uri]

	def intersect(self):
		uris = self.schemes.keys()
		#walk through all schemes and match concepts

	def turtle(self):
		text = head
		for scheme in self.schemes.keys():
			text += self.schemes[scheme].turtle()
		return text

	def dot(self,engine='neato',format='pdf'):
		graphs = []
		for scheme in self.schemes.keys():
			graphs.append(self.schemes[scheme].dot(engine,format))
		return graphs
