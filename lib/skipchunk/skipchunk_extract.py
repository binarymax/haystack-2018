import collections
import spacy
from nltk.corpus import wordnet as wn
nlp = spacy.load('en')

_NNJJ_ = {'JJ','JJR','JJS','NN','NNP','NNS','ADJ','NOUN'} #Nouns and Adjectives
_VBRB_ = {'RB','RBR','RBS','RP','VB','VBD','VBG','VBN','VBP','VBZ','ADV','VERB'} #Verbs and Adverbs
_EXCL_ = {'SP','-RRB-','HYPH'} #Noise to skip
_PUNC_ = {'.',',','?','!',';',':','(',')','[',']','{','}','"','\''} #Punctuation

def parse(filename,encoding):
    txt = open(filename,"r",encoding=encoding).read()
    doc = nlp(txt)
    return doc

def lemmatize(token):
    lemma = token.lower_
    if token.tag_ in _NNJJ_:
        lemma = token.lemma_
    elif token.tag_ in _VBRB_:
        lemma = token.lemma_
    return lemma

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

def printgroup(data):
    for item in data:
        if len(data[item])>1:
            print('--------------------------------------------')
            print(item)
            group = map(lambda x:x[2],data[item])
            coll = collections.Counter(group)
            for c in coll.most_common():
                print('\t',c[1],c[0])

def sortgroup(data):
    items = []
    for item in data:
        if len(data[item])>1:
            group = map(lambda x:x[2],data[item])
            coll = collections.Counter(group)
            total = 0
            pref = None
            for c in coll.most_common():
                if not pref:
                    pref = c[0]
                total += c[1]
            items.append([total,item,pref])
    return sorted(items, key=lambda x:x[0])


def skipchunk_extract(files,maxslop=4,maxlength=4,encoding="utf-8"):
    concepts = dict()
    predicates = dict()
    for file in files:
        doc = parse(file,encoding)
        sentences = annotate(doc)
        concepts,predicates = skipchunk(sentences,maxslop=maxslop,maxlength=maxlength,concepts=concepts,predicates=predicates)
    return concepts,predicates