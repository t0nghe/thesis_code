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

from collections import defaultdict, Counter
import sys
import json
import ast

def grammar_gen(sents):
    """Jeez! I can even run this shit recursively! How cool is that!"""
    grammar = [] # In this set, we store pairs like this (left, right)
    vocab = []
    for sent in sents:
        left = sent[0]
        
        if type(sent[1]) == str:
            right = sent[1]
            grammar.append( (left, right) )
            vocab.append(right)
        else:
            right = [i[0] for i in sent[1:]]
            grammar.append( (left, right) )
            grammar_rec, vocab_rec = grammar_gen(sent[1:])
            grammar.extend(grammar_rec)
            vocab.extend(vocab_rec)

    return grammar, vocab

def grammar_prepare(grammar_list, vocab):
    grammar_set = defaultdict(list)
    terminals = set()
    vocab_count = Counter(vocab)

    # Turn the least common 10 words into UNKs
    uncommon = [i for i, j in vocab_count.most_common()[:-51:-1]]
    non_unks = [word for word in vocab_count.keys() if word not in uncommon]
    for pair in grammar_list:
        l = pair[0]
        r = pair[1]

        if type(r) == str and r in uncommon:
            r = '_UNK_'

        if r not in grammar_set[l]:
            grammar_set[l].append(r)
        if type(r) == str:
            terminals.add(l)

    return dict(grammar_set), list(terminals), non_unks

if __name__ == '__main__':

    tfile = sys.argv[1]
    slug = sys.argv[2]

    sents_list = []
    with open(tfile, 'r') as train:
        for line in train:
            cur_tree = ast.literal_eval(line)
            sents_list.append(cur_tree)

    gra, voc = grammar_gen(sents_list)
    print(gra)
    g, t, v = grammar_prepare(gra, voc)
    
    g_dump = open('grammar_{}.json'.format(slug), 'w')
    t_dump = open('terminals_{}.json'.format(slug), 'w')
    v_dump = open('vocab_{}.json'.format(slug), 'w')

    json.dump(g, g_dump)
    json.dump(t, t_dump)
    json.dump(v, v_dump)

    g_dump.close()
    t_dump.close()
    v_dump.close()