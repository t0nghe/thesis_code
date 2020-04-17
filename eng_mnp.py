# Last checkpoint: mycode_1103.py
# This code takes care of English minimal NPs.

def _readTree(text, ind, verbose=False):
    """Not to be called alone. Used inside `getMinNP()'.
    THIS CODE IS PERFECT. This function is borrowed from:
    https://www.asc.ohio-state.edu/demarneffe.1/LING5050/material/structured.html"""
    if verbose:
        print("Reading new subtree", text[ind:][:10])

    # consume any spaces before the tree
    while text[ind].isspace():
        ind += 1

    if text[ind] == "(":
        if verbose:
            print("Found open paren")
        tree = []
        ind += 1

        # record the label after the paren
        label = ""
        while not text[ind].isspace() and text != "(":
            label += text[ind]
            ind += 1

        tree.append(label)
        if verbose:
            print("Read in label:", label)

        # read in all subtrees until right paren
        subtree = True
        while subtree:
            # if this call finds only the right paren it'll return False
            subtree, ind = _readTree(text, ind, verbose=verbose)
            if subtree:
                tree.append(subtree)

        # consume the right paren itself
        ind += 1
        assert(text[ind] == ")")
        ind += 1

        if verbose:
            print("End of tree", tree)

        return tree, ind

    elif text[ind] == ")":
        # there is no subtree here; this is the end paren of the parent tree
        # which we should not consume
        ind -= 1
        return False, ind

    else:
        # the subtree is just a terminal (a word)
        word = ""
        while not text[ind].isspace() and text[ind] != ")":
            word += text[ind]
            ind += 1

        if verbose:
            print("Read in word:", word)

        return word, ind

def get_eng_mnp(tree: str) -> list:
    """Main function in this file.
    This function takes in Penn bracketing syntactic tree (str).
    And returns all minimal NPs found in the tree in a list of lists.
    
    Eg.:
    
    [ ['Ce', 'travail'], ['recherche'], ['*T*', 'efforts'],
    ['les', 'ex-', "''", 'démocraties', 'populaires', "''"]]
    """
    # STOPTAGS = ['PONCT', 'AP', 'AdP', 'COORD', 'NP', 'VN', 'PP', 'SENT', 'VPpart', 'VPinf', 'Srel', 'Ssub', 'Sint', 'ADV']
    # This variable may not be compulsory. Because the only strong indication
    # of stop is a punctuation mark. Other tags all introduce a subtree. And can be removed by isNested().
    ltree = _readTree(tree, 0)[0]
    nps = _traverseTree(ltree)
    # print('nps', len(nps), nps)

    minimal_nps = []
    for np in nps:
        # For each retrieved NP, either minimal or non minimal,
        # Go through each token in the NP and cut off the NP is certain
        # criteria are met.
        if _isFlat(np):
            # print('We think this NP is flat:', np)
            minimal_nps.append(np)
        else:
            new = []
            for i in np:
                # .startswith() takes in a tuple
                # if _isNested(i) and i[0].startswith( ('SBAR', 'PP', 'ADJP', 'ADVP', 'CC') ):
                if i[0].startswith( ('SBAR', 'PP', 'ADVP', 'CC') ):
                    break
                elif (not _isNested(i)) and _stopPunct(i):
                    break
                else:
                    new.append(i)
            minimal_nps.append(new)
    
    # print('minimal_nps are:', minimal_nps)

    nouns = []
    phrases = []
    for p in minimal_nps:
        if p[0].startswith('NN') and not _isNested(p):
            nouns.append(p)
        else:
            phrases.append(p)
    
    while nouns:
        a = nouns.pop()
        add = True
        for p in phrases:
            if a in p:
                add = False
        if add:
            phrases.append(a)

    # print('nouns are:', nouns)
    # print('phrases are:', phrases)

    stripped_phrases = []
    for phrase in phrases:
        unpacked = _unpack(phrase)
        if unpacked:
            if unpacked[-1] in [',', '.', ';', '!', '?']:
                unpacked.pop()
            if (not stripped_phrases) or (not _phraseIn(unpacked, stripped_phrases[-1])):
                stripped_phrases.append(unpacked)
    return stripped_phrases

def _unpack(np):
    """Helper function called in getMinNP.
    This function takes in a NP as a list. Ideally this shouldn't
    be necessary. But as it transpires, consturcts like: 
    > ['NP-OBJ', ['D', 'de'], ['N', ['A', 'beaux'], ['N', 'jours']]]
    do exist."""
    toks = []
    for item in np:
        if isinstance(item, list):
            if not _isNested(item):
                toks.append(item[-1])
            else:
                toks.extend(_unpack(item))
    return toks

def _stopPunct(tag):
    # Changed from French. Because we don't use PONCT en anglais.
    if not _isNested(tag) and tag[1] in ['-LRB-', '-RRB-', ',']:
        return True

def _isNested(l: list) -> bool:
    """Invoked inside getMinNP.
    This function tells if a NP is nested or not.
    ['PONCT', ','] is not nested."""
    for item in l:
        if isinstance(item, list):
            return True
    return False

def _isFlat(l: list) -> bool:
    """Check if a subtree is flat.
    Takes in ['N', ['N', 'classe'], ['A', 'politique']],
    and returns True. If its not flat, you get False."""
    for item in l[1:]:
        for subitem in item:
            if isinstance(subitem, list):
                return False
    return True

# def _isPhraseNew(shorter, stack):
#     for phrase in stack:
#         if _phraseIn(shorter, phrase):
#             return False
#     return True

def _phraseIn(shorter, longer):
    
    for k in shorter:
        if k not in longer:
            return False
    
    return True

def _traverseTree(ltree: list) -> list:
    """List all NP subtrees in a tree, recursively and return.
    Leave the job of telling with is minimal to getMinNP()."""

    to_return = []

    # The latter condition to account for French phrase eg.
    # "(N (N crise) (P de) (N confiance))"
    if ltree[0].startswith('NP'): 
        to_return.append(ltree)
    # elif (ltree[0] == 'NML') and (len(ltree) > 2 or not _isFlat(ltree)):
    #     to_return.append(ltree)
    
    for subitem in ltree[1:]:
        if isinstance(subitem, list):
            to_return.extend(_traverseTree(subitem))
    
    return to_return

if __name__ == "__main__":

    # Currently testing on samples1103.txt, in which 0-14 are in French
    # the rest are in English.
    with open('english_sample_trees.txt', 'r') as frin:
        lines = frin.readlines()

    lookat = lines[39]

    for np in get_eng_mnp(lookat):
        print('*', np)
