# Code for my implementation of the Earley algorithm.
# This is part of the Syntactic Parsing course in the 
# Language Technology program at Uppsala University.
# Tonghe Wang, 2019

# My implementation of the Earley algorithm includes two components:
# * earley_train.py
# * earley_parse.py

# The training component earley_train.py uses annotated syntactic trees as training data.
# From such training data, it learns production rules from the tree structure, terminals such as POS tags,
# and a vocabulary of most frequent words. Notably, this learning process is not probabilistic. All
# production rules and almost all words that have appeared in the training data are learned.

# The parsing component earley_parse.py uses the learned information to parse input sentences using
# the Earley algorithm. At each turn, it iterates all states in the chart. Since no probabilistic
# information is learned in training, this process is exceedingly tedious. This process is compounded by
# the fact that the Earley algorithm runs on cubic time when parsing.

import sys
import json

class State(object):
    def __init__(self, left, right, dot=0, start=0, end=0, traceback=[]):
        '''Initiate a State object.
        left: left-hand side symbol in a production;
        right: right-hand side symbols;
        dot: current position of dot
        start, end: the span of current state'''
        self.left = left
        self.right = right
        self.traceback = traceback
        self.dot = dot
        self.start = start
        self.end = end

    def next_symbol(self):
        '''Return next symbol after the dot position'''
        return self.right[self.dot]

    def is_complete(self):
        '''Check if this state is completed'''
        return self.dot == len(self.right)

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right and
                self.dot == other.dot and
                self.start == other.start and
                self.end == other.end)

    def __repr__(self):
        symbols = self.right[:]
        symbols.insert(self.dot, '*')
        repr_str = '{} > {} [{}...{}]'.format(
            self.left, ' '.join(symbols), self.start, self.end
        )
        return repr_str

class Earley:
    '''Main block of the Earley parser'''
    def __init__(self, words, grammar, terminals):
        self.chart = [[] for _ in range(len(words) + 1)]
        self.words = words
        self.grammar = grammar
        self.terminals = terminals

    def is_terminal(self, symbol):
        return symbol in self.terminals

    def _enqueue(self, state, chart_index):
        if state not in self.chart[chart_index]:
            self.chart[chart_index].append(state)

    def _predict(self, state):

        B = state.next_symbol()
        j = state.end

        for rule in self.grammar[B]:
            self._enqueue(State(B, rule, 0, j, j), j)

    def _scan(self, state):

        B = state.next_symbol()
        j = state.end

        if self.words[j] in self.grammar[B]:
            self._enqueue(State(B, [self.words[j]], 1, j, j + 1), j + 1)

    def _complete(self, state):

        B = state.left
        j = state.start
        k = state.end

        print('\n\nInside complete:\nCurrent state: {} -> {}'.format(state.left, state.right))

        for st in self.chart[j]:
            if not st.is_complete() and st.next_symbol() == B and st.end == j and st.left != 'gamma':
                # This line changed (How the fuck does trace_back work, shit.)
                self._enqueue(State(st.left, st.right, st.dot + 1, st.start, k, traceback=st.traceback + [state]), k)

    def parse(self):
        cnt = 0
        self._enqueue(State('gamma', ['S'], 0, 0, 0), 0)
        
        for i in range(len(self.words) + 1):
            for state in self.chart[i]:
                if not state.is_complete() and not self.is_terminal(state.next_symbol()):
                    print('{} _predict'.format(cnt))
                    self._predict(state)
                elif i != len(self.words) and not state.is_complete() and self.is_terminal(state.next_symbol()):
                    print('{} _scan'.format(cnt))
                    self._scan(state)
                else:
                    print('{} _complete'.format(cnt))
                    self._complete(state)
                cnt += 1
                

    def __repr__(self):

        repr_str = ''

        for i, chart_entry in enumerate(self.chart):
            repr_str += '\nChart[{}]\n'.format(i)
            
            for state in chart_entry:
                repr_str += str(state) + '\n'

        return repr_str

    def get_top(self):
        length = len(self.words)
        return [st for st in self.chart[-1] if st.is_complete() and st.left == 'S' and st.start == 0 and st.end == length][0]

def build_tree(state, chart):

    tree = [state.left]
    if not state.traceback:
        tree.append(state.right[0])
        return tree
    
    for st in state.traceback:
        subtree = build_tree(st, chart)
        tree.append(subtree)
    return tree

if __name__ == '__main__':

    gfile, tfile, vfile, pfile = sys.argv[1:]

    #print(gfile, tfile, vfile, pfile)

    with open(gfile, 'r') as gin:
        grammar = json.load(gin)
    with open(tfile, 'r') as tin:
        terminals = json.load(tin)
    with open(vfile, 'r') as vin:
        vocab = json.load(vin)
    with open(pfile, 'r') as pin:
        sents = pin.readlines()

    parses = []
    for sent in sents:
        print(sent)
        words = sent.split()

        # Keep track of UNKs in current sentence
        unks = [w for w in words if w not in vocab]

        # Normalize words in current sentence by turning unknown words to _UNK_
        norm_words = [word if word in vocab else '_UNK_' for word in words]

        # Because Jay Earley
        jay = Earley(norm_words, grammar, terminals)
        jay.parse()
        endstate = jay.get_top() # This can be improved by using probability
        tree = json.dumps(build_tree(endstate, jay.chart))
        
        if '_UNK_' in tree:
            tree_sections = tree.split('_UNK_')            
            new_tree = ''
            for i in zip(tree_sections, unks):
                new_tree += i[0]
                new_tree += i[1]
            tree = new_tree

        parses.append(tree+'\n')

    with open(pfile+'.parse', 'w') as pout:
        pout.writelines(parses)