import glob
from topia.termextract import extract
extractor = extract.TermExtractor()

def parse(filename):
    txt = open(filename,"r").read()
    return txt

files = glob.glob("./content/osc/data/*.txt")

text = ""
for filename in files:
	text += parse(filename) + " "
keywords = extractor(text)
best = sorted(keywords,key=lambda x:x[1],reverse=True)
for keyword in best:
	#if keyword[2]>1:
	print(keyword)