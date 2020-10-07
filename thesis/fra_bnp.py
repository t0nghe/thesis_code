def readTree():
# For function readTree(), refer to:
# https://www.asc.ohio-state.edu/demarneffe.1/LING5050/material/structured.html
    pass

def get_fra_mnp(tree: str) -> list:
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
    ltree = readTree(tree, 0)[0]
    nps = _traverseTree(ltree)

    minimal_nps = []
    for np in nps:
        # For each retrieved NP, either minimal or non minimal,
        # Go through each token in the NP and cut off the NP is certain
        # criteria are met.
        if _isFlat(np):
            minimal_nps.append(np)
        else:
            new = []
            for i in np:
                if _isNested(i) and not (i[0] == 'N' or i[0] == 'D'):
                # Nov 5: An earlier version also breaks when the token is a
                # PONCT. But that will exclude NPs like:
                # (NP (D les) (PREF ex-) (PONCT")
                # (N (N démocraties) (A populaires)) (PONCT "))
                # This is arguably a minimal noun phrase, as it's marked.
                # Presumably, only quotation marks will be retained.
                # This phenomenon is arguably only quite visible in French.
                # i[0] == 'D' retains numbers like [4,45%].
                    break
                elif (not _isNested(i)) and _stopPunct(i):
                    break
                else:
                    new.append(i)
            minimal_nps.append(new)
    
    nouns = []
    phrases = []
    for p in minimal_nps:
        if p[0] == 'N' and not _isNested(p):
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
    
    # DONE write YET ANOTHER for-loop to eliminate NPs that
    # end with punctuations other than closing `pair puncts`
    # like:
    # * ['NP-SUJ', ['D', "l'"], ['N', 'IFIL'], ['PONCT', ',']]
    # DONE remove a [N] subtree that already exsits in a [NP].
    # DONE unpack this: ['NP-OBJ', ['D', 'de'], ['N', ['A', 'beaux'], ['N', 'jours']]]
    stripped_phrases = []
    for phrase in phrases:
        unpacked = _unpack(phrase)
        # Add more punctuations on the following line as issues arise
        if unpacked and unpacked[-1] in [',', '.', ';']:
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
    if tag[0] == "PONCT" and tag[1] in ['-LRB-', '-RRB-']:
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
    elif ltree[0] == 'N' and (len(ltree) > 2 or not _isFlat(ltree)):
        # 1105: If a span marked as N and it has more than 2 tokens,
        # or there's a subtree within, get this (N).
        # This retains NPs like this:
        # * ['N', ['A', 'Saint'], ['N', 'Louis']]
        # * (N (N Worms) (C et) (N Cie)) - that is nested in an (AP)
        # But the problem about this is that we'd have:
        # * ['NP', ['N', ['N', 'source'], ['N', 'Perrier']]]
        # * ['N', ['N', 'source'], ['N', 'Perrier']]
        # But this might be solvable or ignorable.
        # Hopefully getMinNP() will take care of this problem,
        # because I tried fixing it by changing this recursion,
        # it picked up way more NPs.
        to_return.append(ltree)
    
    for subitem in ltree[1:]:
        if isinstance(subitem, list):
            to_return.extend(_traverseTree(subitem))

    return to_return

if __name__ == "__main__":

    # Currently testing on samples1103.txt, in which 0-14 are in French
    # the rest are in English.
    with open('samples1103.txt', 'r') as frin:
        lines = frin.readlines()

    lookat = lines[11]
    print(lookat)

    for np in get_fra_mnp(lookat):
        print('*', np)
