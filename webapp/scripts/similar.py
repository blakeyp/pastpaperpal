import os, nltk
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import pandas as pd

# takes paper_id q_num of question to compare to,
# paper_id of paper to compare with,
# and number of top questions to return
# returns (paper_id, q_num) of similar questions
def get_similar_qs(paper_id, q_num, other_papers, get_top):
	
	# list storing text content for each question
	# first add text of question comparing to
	q_texts = [open('media/papers/'+str(paper_id)+'/q'+str(q_num)+'.txt').read()]

	# ordered list of lists each storing paper_id and question_num
	# since this info will be lost when computing tfidf stuff
	# first add paper_id/question comparing to, at index 0
	q_index = [[paper_id,int(q_num)]]

	for paper_id in other_papers:
		paper_dir = 'media/papers/'+str(paper_id)+'/'
		for file in os.listdir(paper_dir):   # traverse paper_id directory
			if file.startswith('q') and file.endswith('.txt'):
				q_texts.append(open(paper_dir + file).read())   # add question content
				q_num = int(file.strip('q.txt'))
				q_index.append([paper_id,q_num])   # keep track of paper_id/q_num for this question

	# qs = []
	# for i in range(len(q_index)*3):
	# 	qs.append(i)
	# print '*****',qs

	# using nltk stopwords (slightly different list?)
	stopwords = nltk.corpus.stopwords.words('english')
	vectorizer = TfidfVectorizer(tokenizer=_tokenize, sublinear_tf=True, stop_words=stopwords)

	# # using default sklearn stopwords list
	# vectorizer = TfidfVectorizer(tokenizer=_tokenize, sublinear_tf=True, stop_words='english')

	# # filtering no stopwords - doesn't perform as well
	# vectorizer = TfidfVectorizer(tokenizer=_tokenize, sublinear_tf=True)

	tfidf_matrix = vectorizer.fit_transform(q_texts)

	print tfidf_matrix
	print vectorizer.get_feature_names()

	# print '****************************** KEYWORDS!!!!!!!!'

	# feature_names = vectorizer.get_feature_names()
	# #print feature_names
	# dense = tfidf_matrix.todense()
	# denselist = dense.tolist()
	# df = pd.DataFrame(denselist, columns=feature_names, index=qs)
	# s = pd.Series(df.loc[2])

	# print s[s > 0].sort_values(ascending=False)[:50]

	# feature_array = np.array(vectorizer.get_feature_names())
	# tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]

	# n = 30
	# top_n = feature_array[tfidf_sorting][:n]

	# print top_n


	pairwise_sim = tfidf_matrix*tfidf_matrix.T   # cosine similarity between texts

	# get pairwise similarity of question with every other question
	# store with retrieved paper_id/q_num using q_index
	# returns list of ([<paper_id>,<q_num>], <pw_sim>) tuples
	pw_sims = []
	for i in range(0,len(q_texts)):
		pw_sims.append((q_index[i], int(pairwise_sim[0,i]*100)))

	# sort to retrieve paper_ids/q_nums of top 4 similar questions
	# note this includes question being compared to (i.e. 100% sim)
	sim_qs = []
	for q, sim in sorted(pw_sims, key=lambda x: x[1], reverse=True)[:get_top+1]:
		print q, sim   # maybe use a measure of similarity?
		sim_qs.append(q)

	return sim_qs

# bespoke tokenizing function for question text
# gets/verifies/lematizes tokens to produce keywords
def _tokenize(text):
	lemmatizer = nltk.WordNetLemmatizer()
	tokens = nltk.word_tokenize(text)
	stems = []
	for tok in tokens:
		if 3<=len(tok)<=20 and not any(ch.isdigit() for ch in tok):
			stems.append(lemmatizer.lemmatize(tok))
	return stems