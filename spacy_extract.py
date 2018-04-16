
# coding: utf-8

# In[1]:

import collections
import spacy
from nltk.corpus import wordnet as wn
nlp = spacy.load('en')


# In[13]:

_NNJJ_ = {'JJ','JJR','JJS','NN','NNP','NNS','ADJ','NOUN'} #Nouns and Adjectives
_VBRB_ = {'RB','RBR','RBS','RP','VB','VBD','VBG','VBN','VBP','VBZ','ADV','VERB'} #Verbs and Adverbs
_EXCL_ = {'SP','-RRB-','HYPH'} #Noise to skip
_PUNC_ = {'.',',','?','!',';',':','(',')','[',']','{','}','"','\''} #Punctuation


# In[3]:

def parse(filename):
    txt = open(filename,"r").read()
    doc = nlp(txt)
    return doc


# In[4]:

def lemmatize(token):
    lemma = token.lower_
    if token.tag_ in _NNJJ_:
        lemma = token.lemma_
    elif token.tag_ in _VBRB_:
        lemma = token.lemma_
    return lemma


# In[5]:

def adj_to_noun(lem):
    for i in wn.synsets(lem, wn.ADJ):
        for j in i.lemmas():
            drf = j.derivationally_related_forms()
            drf.sort(key = lambda x: len(x.name()))
            for k in drf:
                if k.name()[:2] == lem[:2]:
                    #Found it!
                    return k.name()

def noun_to_adj(lem):
    for i in wn.synsets(lem, wn.NOUN):
        for j in i.lemmas():
            for k in j.derivationally_related_forms():
                if k.name()[:2] == lem[:2]:
                    #Found it!
                    return k.name()


# In[6]:

def annotate(doc):
    groups = []
    for sent in doc.sents:
        terms = []
        for tok in sent:
            if tok.tag_ not in _EXCL_:
                lemma = lemmatize(tok)
                drf = None
                #Derive related form:
                if (tok.tag_ == 'JJ'):
                    drf = adj_to_noun(lemma)

                terms.append([tok.norm_,lemma,tok.tag_,drf])
                
        groups.append([sent,terms])
    return groups


# In[28]:

def normalize(stack,origs):
    frm = []
    stack1 = []
    origs1 = []
    
    for tok in stack:
        val = tok[0]
        pos = tok[1]
        if len(tok)>2 and tok[2]:
            val = tok[2]
        if pos in _NNJJ_ or pos in _VBRB_:
            frm.append(val)
        if val not in _PUNC_:
            stack1.append(val)

    i = 0
    j = 0
    k = 0
    f = False
    for tok in origs:
        val = tok[0]
        pos = tok[1]
        j += 1
        if len(tok)>2 and tok[2]:
            val = tok[2]
        if val not in _PUNC_:
            origs1.append(val)
        if pos in _NNJJ_ or pos in _VBRB_:
            i = j
            if not f:
                k = j-1
            f = True
        
            
    origs1 = origs1[k:i]
        
    key = '_'.join(sorted(frm)).lower()
    txt = '_'.join(stack1).lower()
    org = ' '.join(origs1).lower()
    count = len(stack1)
    return key,txt,org,count


# In[29]:

def skipchunk(sentences,maxslop=4,maxlength=4,concepts=dict(),predicates=dict()):
    
    stack = []
    origs = []
    
    def addpredicate():
        nonlocal stack
        nonlocal origs
        key,txt,org,count = normalize(stack,origs)
        if count>1:
            if key not in predicates:
                predicates[key] = []
            predicates[key].append([key,txt,org])
        stack=[]
        origs=[]

    def addconcept():
        nonlocal stack
        nonlocal origs
        key,txt,org,count = normalize(stack,origs)
        if count>1:
            if key not in concepts:
                concepts[key] = []
            concepts[key].append([key,txt,org])
        stack=[]
        origs=[]
    
    for sentence in sentences:
        tokens = sentence[1]

        stack = []
        origs = []
        
        isprd = False
        iscon = False

        last = 0
        slop = 0
        
        for tok in tokens:
            wrd = tok[0]
            lem = tok[1]
            pos = tok[2]
            drf = tok[3]

            if pos in _NNJJ_:
                if isprd:
                    addpredicate()
                    
                last  = 0
                isprd = False
                iscon = True
                stack.append([lem,pos,drf])
                origs.append([wrd,pos,drf])

                if len(stack)>=maxlength:
                    addconcept()

            elif pos in _VBRB_:
                if (iscon):
                    addconcept()
                    
                last  = 0
                isprd = True
                iscon = False
                stack.append([lem,pos])
                origs.append([wrd,pos])

            elif iscon:
                slop += 1
                last += 1

                origs.append([wrd,pos])

                if wrd in _PUNC_ or slop>maxslop:
                    addconcept()
                    iscon = False

            elif isprd:
                slop += 1
                last += 1

                origs.append([wrd,pos])

                if wrd in _PUNC_ or slop>maxslop:
                    addpredicate()
                    isprd = False

    return concepts,predicates


# In[30]:

def printgroup(data):
    for item in data:
        if len(data[item])>1:
            print('--------------------------------------------')
            print(item)
            group = map(lambda x:x[2],data[item])
            coll = collections.Counter(group)
            for c in coll.most_common():
                print('\t',c[1],c[0])


# In[31]:

files = [
    'content/keyword-extraction-datasets/wiki20/documents/10894.txt',
    'content/keyword-extraction-datasets/wiki20/documents/12049.txt',
    'content/keyword-extraction-datasets/wiki20/documents/13259.txt',
    'content/keyword-extraction-datasets/wiki20/documents/16393.txt',
    'content/keyword-extraction-datasets/wiki20/documents/18209.txt',
    'content/keyword-extraction-datasets/wiki20/documents/19970.txt',
    'content/keyword-extraction-datasets/wiki20/documents/20782.txt',
    'content/keyword-extraction-datasets/wiki20/documents/23267.txt',
    'content/keyword-extraction-datasets/wiki20/documents/23507.txt',
    'content/keyword-extraction-datasets/wiki20/documents/23596.txt',
    'content/keyword-extraction-datasets/wiki20/documents/25473.txt',
    'content/keyword-extraction-datasets/wiki20/documents/287.txt',
    'content/keyword-extraction-datasets/wiki20/documents/37632.txt',
    'content/keyword-extraction-datasets/wiki20/documents/39172.txt',
    'content/keyword-extraction-datasets/wiki20/documents/39955.txt',
    'content/keyword-extraction-datasets/wiki20/documents/40879.txt',
    'content/keyword-extraction-datasets/wiki20/documents/43032.txt',
    'content/keyword-extraction-datasets/wiki20/documents/7183.txt',
    'content/keyword-extraction-datasets/wiki20/documents/7502.txt',
    'content/keyword-extraction-datasets/wiki20/documents/9307.txt'   
]
concepts = dict()
predicates = dict()
for file in files:
    doc = parse(file)
    sentences = annotate(doc)
    concepts,predicates = skipchunk(sentences,concepts=concepts,predicates=predicates)


# In[32]:

printgroup(concepts)


# In[33]:

printgroup(predicates)


# In[ ]:



