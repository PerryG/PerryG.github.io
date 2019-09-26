from collections import defaultdict
import random
import re

class Node:
    def __init__(self, is_word = False):
        self.children = defaultdict(Node)
        self.is_word = is_word
        self.__is_winner__ = None

    @property
    def is_winner(self):
        if self.__is_winner__ is None:
            self.__is_winner__ = (not self.is_word) and (not [c for c in self.children.viewvalues() if c.is_winner])
        return self.__is_winner__

class GameTree:
    def __init__(self, dict_path, min_length = 4):
        try:
            self.build_tree(open(dict_path, 'r'), min_length)
        except IOError:
            print 'Invalid dictionary path'
            exit()

    def build_tree(self, d, min_length):
        self.root = Node()
        for word in d:
            # Some stupid thing about \r\n
            word = re.sub('\W+','', word)
            if len(word) < min_length:
                continue
            current = self.root
            for char in word.lower():
                if current.is_word:
                    continue
                current = current.children[char]
            current.is_word = True

    # Returns None if no Node for str, otherwise the Node
    def find_node(self, str):
        current = self.root
        for char in str.lower():
            if current.children.get(char) is None:
                return None
            current = current.children[char]
        return current

    # Returns prefix of the string that is a word if it exists, None otherwise
    def contains_word(self, str):
        current = self.root
        word = ''
        for char in str.lower():
            if current.children.get(char) is None:
                return None
            current = current.children[char]
            word += char
            if current.is_word:
                return word
        return None

    # Given a node, finds a string which completes a word from that node
    def find_suffix(self, node):
        current = node
        str = ''
        while not current.is_word:
            letter, current = current.children.iteritems().next()
            str += letter
        return str

    def print_move(self, str):
        # If it already contains a word, the game is over
        contained = self.contains_word(str)
        if contained is not None:
            print "%s contains a word: %s" % (str, contained)
            return

        # If it's not a prefix, challenge!
        node = self.find_node(str)
        if node is None:
            print '%s is not a prefix to any word. Challenge!' % str
            return

        # If it's not a winning situation already, then you can win!
        if not node.is_winner:
            winning_moves = [k for (k, v) in node.children.viewitems() if v.is_winner]
            letter = random.choice(winning_moves)
            completing_suffix = self.find_suffix(node.children[letter])
            word = str + letter + completing_suffix
            print "You can guarantee a win: Say '%s'. If challenged, a word is %s." % (letter, word)
            return

        # You can't guarantee a win, but maybe you can make them challenge?
        nonword_moves = [k for (k, v) in node.children.viewitems() if not v.is_word]
        if nonword_moves:
            letter = random.choice(nonword_moves)
            completing_suffix = self.find_suffix(node.children[letter])
            word = str + letter + completing_suffix
            print 'You cannot guarantee a win. ' \
                'Why not say \'%s\'? If challenged, a word is %s.' % (letter, word)
            return

        # Oh well, just pick something random
        print 'There is no letter that won\'t form a word, but still is a prefix of a word. '\
            'Pick a random letter, and hope they don\'t challenge.'

def main():
    tree = GameTree('./TWL06.txt')
    while True:
        tree.print_move(raw_input("What letters have been said?\n"))

if __name__ == '__main__':
    main()
