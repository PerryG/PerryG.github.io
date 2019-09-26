from random import random

# f = open('dict.txt', 'r')
f = open('scrabble_dict.txt', 'r')
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',\
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
d = set()

length_two_words = []

for l in f:
    word = l[:-2].lower()
    # word = l[:-1]
    if word.isalpha():
        d.add(word)
    if len(word) == 2:
        length_two_words.append(word)

# Returns a 'chain': list of words which is longest path from root
def longest_chain_from_root(root):
    if root not in d:
        return []
    longest_chain = []
    for letter in alphabet:
        for extension in [letter + root, root + letter]:
            chain = longest_chain_from_root(extension)
            if len(chain) > len(longest_chain) or \
                    (len(chain) == len(longest_chain) and random() > 0.5):
                longest_chain = chain
    return [root] + longest_chain

# print len(d)
# print len(length_two_words)
best_chain = []
for starter in length_two_words:
    chain = longest_chain_from_root(starter)
    if len(chain) > len(best_chain) or (len(chain) == len(best_chain) and random() > 0.5):
        best_chain = chain

for word in best_chain:
    print word