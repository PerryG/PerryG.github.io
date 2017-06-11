from collections import Counter
import os, sys, random

def run_fair(words = None):
	# Returns a set of words
	def get_dict():
		words = set()
		f = open('./TWL06.txt', 'r')
		for word in f:
			words.add(word.upper()[:-2])
		return words
	# Returns a set containing a random word
	def selector(words):
		word = random.sample(words, 1)[0]
		return len(word), set([word])
	# PLays fairly
	def updater(word_set, status, wrong_guesses, guess):
		# Checks if guess is in word, updates status/wrong_guesses
		correct = False
		for i, char in enumerate(random.sample(word_set, 1)[0]):
			if char == guess:
				status[i] = char
				correct = True
		if not correct:
			wrong_guesses.append(guess)
		return word_set, status, wrong_guesses

	if words == None:
		words = get_dict()
	runner(words, selector, updater)

def run_greedy(words = None):
	# Returns a set of words
	def get_dict():
		words = set()
		f = open('./TWL06.txt', 'r')
		for word in f:
			words.add(word.upper()[:-2])
		return words
	# Returns the biggest set of words
	def selector(words):
		# Returns the most common length for set of words
		def most_common_length(words):
			return Counter(map(len, words)).most_common()[0][0]
		length = most_common_length(words)
		return length, filter(lambda x: len(x)==length, words)
	# Acts to restrict the set of words the least (greedily)
	def updater(word_set, status, wrong_guesses, guess):
		# Returns a sketch of where letter appears in word
		def blank_all_but_guess(word):
			return ''.join(map(lambda x: guess if x==guess else '_', word))
		# Returns the most common sketch
		most_words = Counter(map(blank_all_but_guess, word_set)).most_common()[0][0]
		# Checks if guess is in sketch, updates status/wrong_guesses
		correct = False
		for i, char in enumerate(most_words):
			if char != '_':
				status[i] = char
				correct = True
		if not correct:
			wrong_guesses.append(guess)
		# Takes in a sketch, returns a predicate for whether word matches sketch
		def consistent_with_result_func(sketch):
			def word_checker(word):
				for i, char in enumerate(word):
					if (char == guess) !=  (sketch[i] == guess):
						return False
				return True
			return word_checker

		return filter(consistent_with_result_func(most_words), word_set), status, wrong_guesses

	if words == None:
		words = get_dict()
	runner(words, selector, updater)


'''Args:
words: Set of strings. The total dictionary
selector: string set -> int, string set
	Function to get word length initial restricted set
updater: 
	Function to apply after for guess. Arguments:
	word_set, status, wrong_guesses, guess
	word_set: word(s) that might be the correct answer
	status: current status
	wrong_guesses: list of previous wrong guesses
	guess: character

	Returns:
	word_set, status, wrong_guesses'''
def runner(words, selector, updater):
	# The number of unguessed letters in a status
	def unguessed(status):
		return len(filter(lambda x: x=='_', status))
	wrong_guesses = []
	length, word_set = selector(words)
	status = ['_' for i in range(length)]
	while(unguessed(status) != 0):
		# print len(word_set)
		_ = os.system('clear')
		print 'Wrong Guesses: '+', '.join(wrong_guesses)
		print 'Word: '+' '.join(status)
		guess = raw_input('Guess a letter: ').upper()
		while len(guess) > 1 or not guess.isalpha() or guess in wrong_guesses or guess in status:
			print('A guess must be a single letter that you have not already guessed.')
			guess = raw_input('Guess a letter: ').upper()
		word_set, status, wrong_guesses = updater(word_set, status, wrong_guesses, guess)
	_ = os.system('clear')
	print 'Wrong Guesses: '+', '.join(wrong_guesses)
	print 'Word: '+' '.join(status)
	print 'You win! Your score is %d (lower score is better).' % len(wrong_guesses)

if len(sys.argv) == 2:
	if sys.argv[1] == 'greedy':
		run_greedy()
	elif sys.argv[1] == 'fair':
		run_fair()
	else:
		print 'Usage: python hangman.py [greedy/fair]'
else:
	print 'Usage: python hangman.py [greedy/fair]'
