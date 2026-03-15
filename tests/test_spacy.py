import spacy

import spacy.util
import spacy.cli

# Check if "en_core_web_trf" is installed
if not spacy.util.is_package("en_core_web_lg"):
    spacy.cli.download("en_core_web_lg")
    
nlp = spacy.load("en_core_web_lg")
doc = nlp("What is your name? How old are you? Where do you live?")

for token in doc:
    print(token.text, token.pos_, token.morph)
