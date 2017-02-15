import os, re
import numpy as np
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

from keyterms_extractor import getTerms

text_files = sorted(os.listdir('doc_sim'))

documents = [open('doc_sim/'+f).read() for f in text_files]

# X = vectorizer.transform(documents)
# terms = np.array(vectorizer.get_feature_names())
# terms_for_first_doc = zip(terms, X.toarray()[0])



# tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1,3),
#                      min_df = 0, stop_words = 'english', sublinear_tf=True)

# tfidf_matrix = tfidf.fit_transform(documents)

# feature_names = tfidf.get_feature_names()

# doc = 0
# feature_index = tfidf_matrix[doc,:].nonzero()[1]
# tfidf_scores = zip(feature_index, [tfidf_matrix[doc, x] for x in feature_index])

# for w, s in [(feature_names[i], s) for (i, s) in tfidf_scores]:
# 	print w, s

lemmatizer = nltk.WordNetLemmatizer()

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = []
    for tok in tokens:
    	if 3<=len(tok)<=20 and not any(ch.isdigit() for ch in tok):
        	stems.append(tok)
    return stems

from nltk.corpus import stopwords
stopwords = stopwords.words('english')

docs=[]
for i in range(0,15):
	docs.append(str(i)+'.txt')



vectorizer = TfidfVectorizer(tokenizer=tokenize,sublinear_tf=True, stop_words=stopwords)
tfidf_matrix = vectorizer.fit_transform(documents)


# feature_names = vectorizer.get_feature_names()
# dense = tfidf_matrix.todense()
# denselist = dense.tolist()
# df = pd.DataFrame(denselist, columns=feature_names, index=docs)
# s = pd.Series(df.loc['0.txt'])

# print s[s > 0].sort_values(ascending=False)[:50]



# feature_array = np.array(tfidf.get_feature_names())
# tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]

# n = 30
# top_n = feature_array[tfidf_sorting][:n]

# print top_n


# no need to normalize, since Vectorizer will return normalized tf-idf
pairwise_similarity = tfidf_matrix * tfidf_matrix.T

for i in range(0,15):
	for j in range(0,15):
		print '(', i, j, ') :', int(pairwise_similarity[i,j]*100), '%'



# import difflib as dl

# a = file('doc_sim/0.txt').read()
# b = file('doc_sim/b.txt').read()

# sim = dl.get_close_matches

# s = 0
# wa = a.split()
# wb = b.split()

# for i in wa:
#     if sim(i, wb):
#         s += 1

# n = float(s) / float(len(wa))
# print ''
# print '%d%% similarity' % int(n * 100)



# take intersection of keywords lists (incl. mutliple occurences of same word)
# count size of intersection
# normalise by dividing by 2n

# need to define number of keywords to check against i.e. n (e.g. 25)
# n keywords per list
# could be max 2n keywords in intersection
# so divide score by 2n
# resolve to 100% if score greater than this
# 100% sim if no words outside of intersection
# 0% sim if no words inside intersection

# e.g.:
list1 = ['value','value','value','value', 'bit', 'bit','bit', 'statement', 'statement', 'primitive data type', 'primitive data type', 'floating point number', 'code', 'code', 'code', 'byte', 'byte']
list2 = ['value', 'value', 'code','code','code','code', 'bit','bit','bit','bit','bit', 'primitive data type','primitive data type','primitive data type', 'variable', 'variable', 'declaration']

list1 = getTerms('doc_sim/d.txt')
list2 = getTerms('doc_sim/e.txt')

print list1
print list2

set_intersect = set(list1) & set(list2)
list_intersect = [ele for ele in list1+list2 if ele in set_intersect]

print list_intersect, len(list_intersect)

score = len(list_intersect)

diff_paper = False#True
same_q_num = False#True

if diff_paper == True:
	score *= 1.3
if same_q_num == True:
	score *= 1.3

print '\nscore:', int((float(score)/float(len(list1)))*100), '%'   # normalise

# now *hopefully* just need best way to get keywords!
# then how to relate questions and store in db or whatever