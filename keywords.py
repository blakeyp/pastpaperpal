from __future__ import division
import nltk, tfidf, math
from nltk import wordnet
import gensim, re, os

files = ['txt1.txt','txt2.txt','txt3.txt','txt4.txt','txt5.txt','txt6.txt','txt7.txt','txt8.txt','txt9.txt']

texts=[]

def getText(text_file):
    text = ""
    with open(text_file) as f:
        for line in f:
            text += line.strip()+'\n'
    #text = re.sub(r'.*(?:\n.*)*\n1','',text)   # strip all text before start of question 1 - might break!!!
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
        # CON: {<VBD|JJ.*><CC><NP>}   # ... and ... <noun> phrase - how to detect phrases like this

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
        """Normalises words to lowercase and stems and lemmatizes it."""
        word = word.lower()
        #word = stemmer.stem_word(word)
        word = lemmatizer.lemmatize(word)
        return word

    def acceptable_word(word):   # could do tf-idf stuff here? i.e. on individual words
        """Checks conditions for acceptable word: length, stopword."""
        accepted = bool(3 <= len(word) <= 40
            and word.lower() not in stopwords
            and not any(ch.isdigit() for ch in word) )   # deletes words containing digits!
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


# count_terms = [[term,terms.count(term)] for term in set(terms)]

# sort_terms = sorted(count_terms,key=lambda l:l[1], reverse=True)

# for term, count in sort_terms:
#     print term, count

# for term in listKeywords(text):
#     print term


# my tf-idf implementation:

#text1 = getText(files[0])
#print getCandidates(text1)


#print getCandidates(getText('texts/txt9.txt'))



texts=[]

for text_file in os.listdir('../pastpapers/astext'):
    texts.append(getCandidates(getText('../pastpapers/astext/'+text_file)))   # list of lists of candidate keywords



# see branch 'try' for gensim implementation of tf-idf which might be better
def getKeywords(text, texts):   # text as list of candidate keywords, texts as list of lists of candidate keywords

    #candidates = getCandidates(text)

    def tf(keyword, text):   # term frequency
        #print keyword, text.count(keyword), len(text)
        return text.count(keyword) / len(text)

    def numContaining(keyword, texts):   # number of lists containing keyword
        return sum(1 for text in texts if keyword in text)

    def idf(keyword, texts):
        return math.log(len(texts) / (1 + numContaining(keyword,texts)))

    def tfidf(keyword, text, texts):
        return tf(keyword,text) * idf(keyword,texts)

    scores = {candidate: tfidf(candidate, text, texts) for candidate in text}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # for word, score in sorted_words:
    #     print word, score

    keywords=''

    for candidate in text:   # gives top 30 keywords in order of appearance in paper
        if any(candidate in word_score for word_score in sorted_words[:30]) and (candidate not in keywords):
            keywords += candidate+', '

    #keywords.rstrip(', ')


    g = open('../keywords/keywords.txt', 'w')

    g.write(keywords[:-2])
    g.close()

    return

getKeywords(texts[12], texts)


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