#py script for information retrieval coursework 1

import xml.etree.ElementTree as ET
import re
import nltk
from nltk.stem import PorterStemmer
import math
import operator

#pre-process the given text
def preprocess(text):
	preprocessedtokens=[]
	stopwordsfile = open(r'C:\Users\pyath\Documents\Edinburgh\TTDS\CW1\EnglishStopWords.txt','r')
	stopwords = stopwordsfile.read().split()
	tokens = re.split(r"[ ,.:;></|+-@#!$%^&*_=\n\'\"\[\]\{\}\(\)]", text) #tokenisation
	for token in tokens:
		if token.lower() not in stopwords and token !='': #stopping
			token.lower() #case-folding
			porter = PorterStemmer()
			stemmedtoken = porter.stem(token) #porter-stemming
			if stemmedtoken.lower() not in stopwords: #stopping
				preprocessedtokens.append(stemmedtoken)
	return preprocessedtokens

#positional inverted index
pii={}

#parse the given documents and generate positional inverted index
listofdocs=[]
tree = ET.parse('trec.5000.xml')
root = tree.getroot()
for doc in root:
	stringtopreprocess = ""
	docbeingprocessed = 0
	for subdoc in doc:
		if subdoc.tag == "DOCNO":
			docbeingprocessed = subdoc.text
			listofdocs.append(docbeingprocessed)
		if subdoc.tag == "HEADLINE":
			stringtopreprocess+=subdoc.text
		if subdoc.tag=="TEXT":
			stringtopreprocess+=subdoc.text
	#pre-process the text(headline+text)
	tokens = preprocess(stringtopreprocess)
	#evaluate every token to generate index
	for pos,token in enumerate(tokens):
		#if token exists in our index
		if token in pii:
			#if the token exists in the doc
			if docbeingprocessed in pii[token][1]:
				pii[token][1][docbeingprocessed].append(pos)
			else:
				pii[token][0] += 1
				pii[token][1][docbeingprocessed] = [pos]
		#if we see the token for the first time
		else:
			pii[token] = []
			#set initial frequency to 1
			pii[token].append(1)
			pii[token].append({})
			#append the document number
			pii[token][1][docbeingprocessed] = [pos]

#print the positional inverted index in a file
posinvindexfile = open(r'C:\Users\pyath\Documents\Edinburgh\TTDS\CW1\index.txt','w')
for key in pii:
	posinvindexfile.write(str(key) +':'+str(pii[key][0]))
	posinvindexfile.write('\n')
	for skey in pii[key][1]:
		posinvindexfile.write('\t'+ str(skey) + ':' + str(pii[key][1][skey]).replace('[','').replace(']',''))
		posinvindexfile.write('\n')
posinvindexfile.close()

#boolean search evaluation
queryresults = open(r'C:\Users\pyath\Documents\Edinburgh\TTDS\CW1\results.boolean.txt','w')
porter = PorterStemmer()

#boolean operations helper methods
def finddocuments(word):
	return pii[str(word)][1]

def AND_op(doc1, doc2):
	return sorted(doc1.keys() & doc2.keys())

def OR_op(doc1, doc2):
	return sorted(doc1.keys() | doc2.keys())

def NOT_op(doc):
	return sorted(listofdocs - doc.keys())

def ANDNOT_op(doc1, doc2):
	return sorted(doc1.keys() - doc2.keys())

def ORNOT_op(doc1, doc2):
	return sorted(doc1.keys() | (listofdocs-doc2.keys()))

#proximity search
def proximitysearch(query):
	startingindex = query.index('(')
	proximity = str(query[1:startingindex])
	docsfound=[]
	words = query[startingindex+1:len(query)-2].split(',')
	docs = AND_op(finddocuments(porter.stem(words[0].strip())), finddocuments(porter.stem(words[1].strip())))
	for doc in docs:
		found=False
		word1pos = pii[porter.stem(words[0]).strip()][1][doc]
		word2pos = pii[porter.stem(words[1]).strip()][1][doc]
		for i in word1pos:
			for j in word2pos:
				if(abs(j-i)<=int(proximity)): #find words in given proximity
					docsfound.append(doc)
					found = True
					break
			if found is True:
				found = False
				break
	return docsfound

#retrieve tokens in phrases
def retrievephrasetokens(phrase):
	firstindex = query.index(r'"')
	secondindex= query.index(r'"', firstindex+1)
	return query[firstindex+1:secondindex].split()

#phrase search
def phrasesearch(query):
	if("AND" not in query and "OR" not in query and "NOT" not in query):#phrase with no booleans
		words = retrievephrasetokens(query)
		return phrasesearchutil(words)
	elif("AND NOT" in query):
		if(query[0]=='\"' and query[len(query)-2]=='\"'):#check if we have two phrases
			phrases = query.split("AND NOT")
			phrase1docs = phrasesearchutil(retrievephrasetokens(phrases[0]))
			phrase2docs = phrasesearchutil(retrievephrasetokens(phrases[1]))
			docs = ANDNOT_op(phrase1docs, phrase2docs)
			return docs
		elif(query[0]=='\"'):#if phrase comes first in the query
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = ANDNOT_op(phrasedocs, finddocuments(porter.stem(query.split()[len(query.split())-1])))
			return docs
		else:#if phrase comes last in the query
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = ANDNOT_op(finddocuments(porter.stem(query.split()[0])), phrasedocs)
			return docs
	elif("OR NOT" in query):
		if(query[0]=='\"' and query[len(query)-2]=='\"'):
			phrases = query.split("OR NOT")
			phrase1docs = phrasesearchutil(retrievephrasetokens(phrases[0]))
			phrase2docs = phrasesearchutil(retrievephrasetokens(phrases[1]))
			docs = ORNOT_op(phrase1docs, phrase2docs)
			return docs
		elif(query[0]=='\"'):
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = ORNOT_op(phrasedocs, finddocuments(porter.stem(query.split()[len(query.split())-1])))
			return docs
		else:
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = ORNOT_op(finddocuments(porter.stem(query.split()[0])), phrasedocs)
			return docs
	elif("AND" in query):
		if(query[0]=='\"' and query[len(query)-2]=='\"'):
			phrases = query.split("AND")
			phrase1docs = phrasesearchutil(retrievephrasetokens(phrases[0]))
			phrase2docs = phrasesearchutil(retrievephrasetokens(phrases[1]))
			docs = AND_op(phrase1docs, phrase2docs)
			return docs
		elif(query[0]=='\"'):
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = AND_op(phrasedocs, finddocuments(porter.stem(query.split()[len(query.split())-1])))
			return docs
		else:
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = AND_op(finddocuments(porter.stem(query.split()[0])), phrasedocs)
			return docs
	elif("OR" in query):
		if(query[0]=='\"' and query[len(query)-2]=='\"'):
			phrases = query.split("OR")
			phrase1docs = phrasesearchutil(retrievephrasetokens(phrases[0]))
			phrase2docs = phrasesearchutil(retrievephrasetokens(phrases[1]))
			docs = OR_op(phrase1docs, phrase2docs)
			return docs
		elif(query[0]=='\"'):
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = OR_op(phrasedocs, finddocuments(porter.stem(query.split()[len(query.split())-1])))
			return docs
		else:
			words = retrievephrasetokens(query)
			phrasedocs = phrasesearchutil(words)
			docs = OR_op(finddocuments(porter.stem(query.split()[0])), phrasedocs)
			return docs

#helper method for phrase search
def phrasesearchutil(words):
	docsfound={}
	docs = AND_op(finddocuments(porter.stem(words[0].strip())), finddocuments(porter.stem(words[1].strip())))
	for doc in docs:
		found=False
		word1pos = pii[porter.stem(words[0]).strip()][1][doc]
		word2pos = pii[porter.stem(words[1]).strip()][1][doc]
		for i in word1pos:
			for j in word2pos:
				if(j-i==1):
					docsfound[doc] = ""
					found = True
					break
			if found is True:
				found = False
				break
	return docsfound

#boolean search queries and results
with open(r'C:\Users\pyath\Documents\Edinburgh\TTDS\CW1\queries.boolean.txt','r') as queriesfile:
	for line in queriesfile:
		queryno = line[:line.index(" ")]
		query = line[line.index(" ")+1:]
		if(query[0]=='#'):#if proximity search
			docs = proximitysearch(query)		
			for doc in docs:
				queryresults.write(queryno+','+doc+'\n')
		elif("\"" in query):#if phrase search
			docs = phrasesearch(query)
			for doc in docs:
				queryresults.write(queryno+','+doc+'\n')
		elif(len(query.split())==1):#if search is a single word
			for key in pii[porter.stem(query.strip())][1]:
				queryresults.write(queryno+','+key+'\n')
		elif("AND NOT" in query):
			docs = ANDNOT_op(finddocuments(porter.stem(query.split()[0])), finddocuments(porter.stem(query.split()[len(query.split())-1]))) 
			for doc in docs:
				queryresults.write(queryno+','+doc+'\n')
		elif("OR NOT" in query):
			docs = ORNOT_op(finddocuments(porter.stem(query.split()[0])), finddocuments(porter.stem(query.split()[len(query.split())-1]))) 
			for doc in docs:
				queryresults.write(queryno+','+doc+'\n')
		elif("AND" in query):
			docs = AND_op(finddocuments(porter.stem(query.split()[0])), finddocuments(porter.stem(query.split()[len(query.split())-1]))) 
			for doc in docs:
				queryresults.write(queryno+','+doc+'\n')
		elif("OR" in query):
			docs = ORNOT_op(finddocuments(porter.stem(query.split()[0])), finddocuments(porter.stem(query.split()[len(query.split())-1]))) 
			for doc in docs:
				queryresults.write(queryno+','+doc+'\n')
queriesfile.close()

#ranked retrieval
rankedresultsfile = open(r'C:\Users\pyath\Documents\Edinburgh\TTDS\CW1\results.ranked.txt','w')
def idocumentfrequency(word):
	N = len(listofdocs)
	df = pii[word][0]
	return math.log10(N/df)

def termfrequency(doc, word):
	if doc in pii[word][1]:
		tf = len(pii[word][1][doc])
		return 1+math.log10(tf)
	return 0

def tfidf(doc, words):
	tfidf = 0
	for word in words:
		tfidf += idocumentfrequency(word) * termfrequency(doc, word)
	return tfidf

with open(r'C:\Users\pyath\Documents\Edinburgh\TTDS\CW1\queries.ranked.txt','r') as rankedqueries:
	MAX_RESULTS = 150
	rankedqueryresults = {}
	for line in rankedqueries:
		queryno = line[:line.index(" ")]
		query = line[line.index(" ")+1:]
		tokens = preprocess(query)
		querydocs={}
		for token in tokens:
			docs = finddocuments(token)
			for doc in docs:
				if doc not in querydocs:
					querydocs[doc] = 0
		for doc in querydocs:
			querydocs[doc]=tfidf(doc, tokens)
		querydocs = dict(sorted(querydocs.items(), key=operator.itemgetter(1), reverse=True))
		querydocs = dict(list(querydocs.items())[:MAX_RESULTS])
		rankedqueryresults[queryno] =querydocs
	for queryno in rankedqueryresults:
		for rankeddoc in rankedqueryresults[queryno]:
			rankedresultsfile.write(str(queryno.strip())+','+str(rankeddoc)+','+str(rankedqueryresults[queryno][rankeddoc])+'\n')
	rankedresultsfile.close()
rankedqueries.close()



