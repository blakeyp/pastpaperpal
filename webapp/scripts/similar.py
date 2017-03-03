import os, nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# takes paper_id/q_num of question to compare to,
# paper_ids of papers to compare with,
# and number of top questions to return
# returns (paper_id, q_num) of similar questions
def get_similar_qs(paper, q_num, other_papers, get_top):
	
	# list storing text content for each question
	# insert text of question comparing to first
	q_texts = [open('media/papers/'+str(paper)+'/q'+str(q_num)+'.txt').read()]

	# ordered list of lists each storing paper_id and question_num
	# since this info will be lost when computing tfidf stuff
	# paper/question comparing to will be at index 0
	q_index = [[paper,int(q_num)]]

	for paper in other_papers:
		root = 'media/papers/'+str(paper)+'/'
		for file in os.listdir(root):   # traverse paper directory
			if file.startswith('q') and file.endswith('.txt') and 'n' not in file:
				q_texts.append(open(root+file).read())   # add question content
				q_num = int(file.strip('q.txt'))
				q_index.append([paper,q_num])   # keep track of paper_id/q_num for this question

	stopwords = nltk.corpus.stopwords.words('english')
	vectorizer = TfidfVectorizer(tokenizer=_tokenize,sublinear_tf=True, stop_words=stopwords)
	tfidf_matrix = vectorizer.fit_transform(q_texts)
	pairwise_sim = tfidf_matrix*tfidf_matrix.T   # cosine similarity between texts

	# get pairwise similarity of question with every other question
	# store with retrieved paper/q_num using q_index
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