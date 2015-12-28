import sys
import os
import pymongo
from pymongo import MongoClient
import bson
from time import mktime
from datetime import datetime , timedelta
import pprint
import hashlib
import feedparser
import nltk
import math
import operator
import numpy
from hcluster import linkage, dendrogram

'''
pick news items of previous 3 days
tf-df implementation
'''
news_order 		= ['telegraph','sky','independent','dailymail','guardian','bbc','espn']

def freq(word,doc):
	return doc.count(word)

def wordCount(doc):
	return len(doc)

def docWithWord(word,docList):
	res	=0
	for doc in docList:
		if freq(word,doc) > 0:
			res	= res+1

	return res

def tf(word,doc):
	return freq(word,doc)/float(wordCount(doc))

def idf(word,docList):
	return math.log(len(docList)/docWithWord(word,docList))

def tfidf(word,doc,docList):
	return tf(word,doc)*idf(word,docList)

def getTopKeyWords(n,doc,corpus):
	'''
		for each word in doc calculate its tf-idf
	'''

	tfidfMap 		= {}
	for word in set(doc):
		tfidfMap[word] = tfidf(word,doc,corpus)

	sorted_tfidfMap	= sorted(tfidfMap.iteritems(), key=operator.itemgetter(1))	
	sorted_tfidfMap.reverse()
	return [w[0] for w in sorted_tfidfMap[:n]]   	

def extract_clusters(Z,threshold,n):
   clusters={}
   ct=n
   for row in Z:
      if row[2] < threshold:
          n1=int(row[0])
          n2=int(row[1])

          if n1 >= n:
             l1=clusters[n1] 
             del(clusters[n1]) 
          else:
             l1= [n1]
      
          if n2 >= n:
             l2=clusters[n2] 
             del(clusters[n2]) 
          else:
             l2= [n2]    
          l1.extend(l2)  
          clusters[ct] = l1
          ct += 1
      else:
          return clusters

connection 			= MongoClient('127.0.0.1', 27017,j=True)
db 					= connection.news_aggregator


dt 					= 	datetime.utcnow() - timedelta(days=3)
cursor				=   db.news.find({'created_date':{'$gte':dt}}).sort([('created_date',pymongo.DESCENDING)])

corpus				=   []
news_object			=   []
title				=   []
source				=   []
date_time			=   []


for record in cursor:
	Obj				= []
	Obj.extend(record['summary'])
	Obj.extend(record['title'])
	corpus.append(Obj)
	news_object.append(record)


key_word_list		=	set()
keyWordsPreDoc		=   4

for doc in corpus:
	word_list 		=   getTopKeyWords(keyWordsPreDoc,doc,corpus)
	for w in word_list:
		key_word_list.add(w)


'''
feature vector for all news articles
'''

feature_vector		= []
corpus_length		= len(corpus)

for doc in corpus:
	vect 			= []
	for word in key_word_list:
		if word in doc:
			vect.append(tfidf(word,doc,corpus))
		else:
			vect.append(0)

	feature_vector.append(vect)


sim_matrix			= numpy.empty((corpus_length,corpus_length))
for i in xrange(0,corpus_length):
	for j in xrange(0,corpus_length):
		sim_matrix[i][j] = nltk.cluster.util.cosine_distance(feature_vector[i],feature_vector[j])


sim_threshold			 	= 0.8
Z 							= linkage(sim_matrix, 'single')
clusters 					= extract_clusters(Z,sim_threshold,corpus_length)
sorted_clusters				= sorted(clusters, key=lambda y: len(clusters[y]),reverse=True)

for key in sorted_clusters:
   sorted_news_order		= sorted(clusters[key],key=lambda x: news_order.index(news_object[x]['source']))
   for id in sorted_news_order:
       print id," ".join(news_object[id]['title']),news_object[id]['source'],news_object[id]['created_date']
   
   print "----------------------------------------"
