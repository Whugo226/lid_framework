######### JOHN OLAFENWA AND MOSES OLAFENWA ##########
#www.github.com/johnolafenwa/Ling10

Ling10-trainlarge contains 190 000 sentences in 10 languages
English, French, Portugese, Chinese Mandarin, Russian, Hebrew, Polish, Japanese, Italian, Dutch

File Descriptions
#train_set.txt
	Contains 140 000 sentences, divided into 14 000 sentences per language class
        Contains integer labels for each sentence



#test_set.txt
	Contains 50 000 sentences, divided into 5000 sentences per language class
	Contains integer labels for each sentence
	

Both the train and test files are organized as sentence - label pairs with the tab characer "\t" separating them.

#chars.json
	A single json file containing two arrays: "char_to_idx" mapping characters to Integers and "idx_to_char" mapping Integers to characters

#languagemap.json
	A json file mapping Integer labels to the languages they represent
