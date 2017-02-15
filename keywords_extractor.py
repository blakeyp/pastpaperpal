from __future__ import division
import nltk, tfidf, math
from nltk import wordnet
import gensim, re, os
from collections import Counter

#files = ['txt1.txt','txt2.txt','txt3.txt','txt4.txt','txt5.txt','txt6.txt','txt7.txt','txt8.txt','txt9.txt']

#texts=[]

def getText(text_file):
    text = ""
    with open(text_file) as f:
        for line in f:
            text += line.strip()+'\n'
    text = re.sub(r'-\n','',text)   # resolve hyphentation
    text = re.sub(r'{(?:[^}{]|{(?:[^}{]|{[^}{]*})*})*}','',text)   # attempt to remove code snippets! - more clever method?
    text = "".join(char for char in text if ord(char) < 128)   # remove non-ascii characters
    return text

def getCandidates(text):

    lemmatizer = nltk.WordNetLemmatizer()
    stemmer = nltk.stem.porter.PorterStemmer()

    grammar = r'''
        NP: {<JJ.*><NN.*><NN.*>?<NN.*>?}   # adjective-noun phrase
            {<NN.*><NN.*>?<NN.*>?}   # sequence of nouns
    '''

    chunker = nltk.RegexpParser(grammar)

    toks = nltk.word_tokenize(text)

    postoks = nltk.tag.pos_tag(toks)

    tree = chunker.parse(postoks)

    def leaves(tree):   # return leaves of each noun phrase subtree of chunked tree
        leaves = []
        for subtree in tree.subtrees():
            if subtree.label() == 'NP':
                leaves.append(subtree.leaves())
                #print subtree.leaves()
        return leaves

    from nltk.corpus import stopwords
    stopwords = stopwords.words('english')

    my_stopwords = ['state','define','show','describe','explain','find','compare','contrast','determine','answer','answers','part','parts','section','sections','following','continued','mark','marks']   # maybe chop off if at front of sentence?
    stopwords.extend(my_stopwords)

    #print stopwords

    def normalise(word):
        """Normalises words to lowercase and lemmatizes it."""
        word = word.lower()
        word = lemmatizer.lemmatize(word)
        return word

    def acceptable_word(word):
        """Checks conditions for acceptable word: length, stopword."""
        accepted = bool(4 <= len(word) <= 20
            and word.lower() not in stopwords
            and not any(ch.isdigit() for ch in word))
        return accepted

    def get_terms(tree):
        terms = []
        for leaf in leaves(tree):   # traverse leaves in each subtree
            term = ''
            for word, tag in leaf:   # traverse words in leaf
                if acceptable_word(word):
                    term += normalise(word)+' '   # make term out of words
            if (term != ''):
                terms.append(term.strip())   # add term to list
        return terms

    candidates = get_terms(tree)

    return candidates

def getTerms(text):

    terms = getCandidates(getText(text))

    #print terms

    terms.sort(key=Counter(terms).get, reverse=True)

    #return [item for items, c in Counter(terms).most_common() for item in [items] * c][:25]

    print "******", terms

    count_terms = [[term,terms.count(term)] for term in set(terms)]

    sort_terms = sorted(count_terms,key=lambda l:l[1], reverse=True)

    terms=[]
    for term, count in sort_terms[:25]:
        print term
        terms.append(term)#print term, count

    return terms#sort_terms[:25]


getTerms('doc_sim/0.txt')
    #for term in listKeywords(text):
    #     print term


    # my tf-idf implementation:

    #text1 = getText(files[0])
    #print getCandidates(text1)


    #print getCandidates(getText('texts/txt9.txt'))



def compare_keywords(list1, list2):

    list3 = list(set(list1)&set(list2))

    print '*****'
    print list3

    print len(list3)
    print len(set(list1))

    y = float(len(list3))/float(len(set(list1)))
    print '%d%%' % int(y*100)

    list3=[]





    score = 0
    for i in list2:
        if i in list1:
            score += 1

    score_of_list1 = float(score*100)/float(len(list1))


    score = 0
    for i in list1:
        if i in list2:
            score += 1

    score_of_list2 = float(score*100)/float(len(list2))

    print score_of_list1, score_of_list2

    print "*******", int((score_of_list1+score_of_list2)/2)


    score = 0
    for word1 in list1:
        for word2 in list2:
            if word1 == word2:
                if word1 in list3 or word2 in list3:
                    score += 1
                else:
                    score += 5
                list3.append(word1)
    n = float(score) / float((len(list1)*len(list2)))
    print '%d%%' % int(n*100)


# comparing question text for similarity:
# if more important (higher occuring) keywords match



# texts=[]

# for text_file in os.listdir('../pastpapers/astext'):
#     texts.append(getCandidates(getText('../pastpapers/astext/'+text_file)))   # list of lists of candidate keywords



# # see branch 'try' for gensim implementation of tf-idf which might be better
# def getKeywords(text, texts):   # text as list of candidate keywords, texts as list of lists of candidate keywords

#     #candidates = getCandidates(text)

#     def tf(keyword, text):   # term frequency
#         #print keyword, text.count(keyword), len(text)
#         return text.count(keyword) / len(text)

#     def numContaining(keyword, texts):   # number of lists containing keyword
#         return sum(1 for text in texts if keyword in text)

#     def idf(keyword, texts):
#         return math.log(len(texts) / (1 + numContaining(keyword,texts)))

#     def tfidf(keyword, text, texts):
#         return tf(keyword,text) * idf(keyword,texts)

#     scores = {candidate: tfidf(candidate, text, texts) for candidate in text}
#     sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)

#     # for word, score in sorted_words:
#     #     print word, score

#     keywords=''

#     for candidate in text:   # gives top 30 keywords in order of appearance in paper
#         if any(candidate in word_score for word_score in sorted_words[:30]) and (candidate not in keywords):
#             keywords += candidate+', '

#     #keywords.rstrip(', ')


#     g = open('../keywords/keywords.txt', 'w')

#     g.write(keywords[:-2])
#     g.close()

#     return







#getKeywords(texts[12], texts)


# imported tfidf implemtation - seems to work differently:

# dictionary = gensim.corpora.Dictionary(keywords)   # (keyword, id) pairs

# corpus = [dictionary.doc2bow(text) for text in keywords]   # (id, count) pairs

# tfidf = gensim.models.TfidfModel(corpus)
# corpus_tfidf = tfidf[corpus]   # returns lists of (id, tf-idf) pairs

# corpus_tfidf = list(corpus_tfidf)   # make list of lists

# d = {}; tfidfss=[]

# for id, value in corpus_tfidf[<specific list here>]:
#   word = dictionary.get(id)
#   d[word] = value
#   tfidfss.append((word, d[word]))

# tfidfss.sort(key=lambda x: x[1], reverse=True)

# for word,tfidf in tfidfss:
#     print word,tfidf