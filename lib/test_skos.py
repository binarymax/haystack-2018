#test_skos.py
from skos import SKOS 

kos = SKOS()
scheme1 = kos.scheme(u'http://example.com/test1-scheme',u'Test1 Scheme','test1-scheme')
concept1 = scheme1.concept(u'http://example.com/test1-concept',u'test1-concept')
concept1.label(u'Hello',u'en',isPref=True)
concept1.label(u'Howdy',u'en')
concept1.label(u'Aloha',u'haw')

scheme2 = kos.scheme(u'http://example.com/test2-scheme',u'Test2 Scheme','test2-scheme')
concept2 = scheme2.concept(u'http://example.com/test2-concept',u'test2-concept')
concept2.label(u'Hello',u'en',isPref=True)
concept2.label(u'Howdy',u'en')
concept2.label(u'Aloha',u'haw')

print(kos.turtle())
