from collections import defaultdict

class Tree:

    """This Class needs to do the following:
    1) represent the inner structure of a UD tree, both for English and French.
        a) take care of clitics in French.
        - How are relations marked with clitics? Eg, with `*T*' or `du'?
            - all relations go to original forms. Eg. There's nothing for `du', but there are things for `de' and `le'.
    2) able to load original UD files and extended UD files.
        - One column is added at the end (column 11 at index 10) dubbed `BNP'.

    * The following features can only be called when the tree is tagged with BIO.

    3) able to output needed features in either
        a) category names in TSV; or
        b) integers in TSV.
        - the latter requires listing and mapping all categories.
        - each token also needs to keep a list of children.
        - This function 
    x） in connection with the features needed in the NN:
        a) POS of parent token; deprel with that token;
        b) POS of parent and grand parent tokens; deprels with those tokens;
        c) POS of parent token... etc...
        d) deprel with previous and next...

    * Morphological features:
        - What morphs are universal to all POS? (Gender and number!!!)

    * When we output a BNP-marked tree, the combined lines in a UD will be discarded.
    """

    class Token:

        def __init__(self, idx, form, lemma, pos, xpos, feats, head, rel, deps, misc, bnp=None):
            """Takes in a tuple of attributes"""
            self.idx = idx
            self.form = form  # Column 2
            self.lemma = lemma  # Column 3
            self.pos = pos  # Column 4
            self.xpos = xpos
            self.feats = feats
            self.head = head  # Column
            self.rel = rel  # Column which
            self.deps = deps
            self.misc = misc
            self.bnp = bnp # When we mark a Token in the span of a minimal NP, we change this to 'B' or "I" or "O"
            self.nnfeat = None

        def _get_mf(self):
            """Returns gender and number of a token. Masc vs Fem. Plur vs Sing.
            If either is absent, an underscore is given."""
            if self.feats != '_':
                cols = self.feats.split('|')
                feats_dict = dict()
                for i in cols:
                    k, v = i.split('=')
                    feats_dict[k] = v

                d = feats_dict['Definite'] if 'Definite' in feats_dict else '_'
                g = feats_dict['Gender'] if 'Gender' in feats_dict else '_'
                n = feats_dict['Number'] if 'Number' in feats_dict else '_'
                pt = feats_dict['PronType'] if 'PronType' in feats_dict else '_'
                p  = feats_dict['Person'] if 'Person' in feats_dict else '_'
                ps = feats_dict['Poss'] if 'Poss' in feats_dict else '_'
                nt = feats_dict['NumType'] if 'NumType' in feats_dict else '_'
                c = feats_dict['Case'] if 'Case' in feats_dict else '_'

                return  d,   g,   n,   pt,  p,   ps,  nt,  c
            else:
                return '_', '_', '_', '_', '_', '_', '_', '_'
            
            
        def is_dep_prev(self):
            """If this Token is a dep of previous Token"""
            return True if self.idx - self.head == 1 else False

        def is_dep_next(self):
            """If this Token is a dep of next Token"""
            return True if self.idx - self.head == -1 else False

        def __repr__(self):
            return '{} "{}"'.format(self.idx, self.form)

        # TODO Implement other methods to output other trainable features,
        # will be called `nnfeat' to distinguish from morphological features.

    def __init__(self, string, bnp_marked=False):
        """Initialize the object from a string represents a tree"""
        self.tokens = {}  # A dictionary that organizes tokens
        self.children = defaultdict(list) 

        self.sentid_line = ''
        for l in string.split('\n'):
            if l.startswith("# sent_id"):
                self.sentid_line = l
            if len(l) > 0 and not l.startswith(('#', '"')):
                cols = l.split('\t')
                try:
                    idx = int(cols[0])
                except ValueError:
                    continue
                form = cols[1]
                lemma = cols[2]
                pos = cols[3]
                xpos = cols[4]
                feats = cols[5]
                head = int(cols[6])
                rel = cols[7]
                deps = cols[8]
                misc = cols[9]
                if bnp_marked:
                    bnp = cols[10] # TODO Change this line to reflect re
                    self.tokens[idx] = self.Token(idx, form, lemma, pos, xpos, feats, head, rel, deps, misc, bnp)
                else:
                    self.tokens[idx] = self.Token(idx, form, lemma, pos, xpos, feats, head, rel, deps, misc)
                self.children[head].append(idx)

        # This may not be necessary if we implement a method.
        self.bnp_marked = bnp_marked 

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, k):
        # Forgot how __getitem__() is used.
        """Gets token at ID k. Note this is 1-based,
        as in CoNLLU files."""
        if k == 0:
            # This is just for the 
            return self.Token(0, 'ROOT', '_', '_', '_', '_', '_','_','_', '_')
        else:
            return self.tokens[k]
        
    def __iter__(self):
        for i in self.tokens.values():
            yield i

    def list_forms(self):
        forms = []
        for i in self.tokens:
            forms.append(self.tokens[i].form)
        return forms

    def list_lemmas(self):
        # This way the first real lemma will be indexed at 1.
        # Less confusing when loading trees.
        lemmas = []
        for i in self.tokens:
            lemmas.append(self.tokens[i].lemma)
        return lemmas

    def list_bios(self):
        bios = []
        for i in self.tokens:
            bios.append(self.tokens[i].bnp)
        return bios

    def list_pos(self):
        lpos = ['ROOT']
        for i in self.tokens:
            lpos.append(self.tokens[i].pos)
        return lpos

    def _match(self, phrase, toks):
        """Compares if a and b matches.
        If one of them is `le' and the other `*T*',
        they are a match."""
        # DONE List cases of matching tokens
        match = []
        for word, tok in zip(phrase, toks):
            if word == tok.form:
                match.append(True)
            # This 'DET' condition is already quite permissive.
            elif word == '*T*' and tok.pos == 'DET':
                match.append(True)
            else:
                match.append(False)
        return all(match)

    def load_bnp(self, phrases):
        """phrases: a list that contains phrases in the form of lists"""
        # [['cet', 'éclatement'], ["l'", 'audience'], ['qui'], ['la', 'hantise'], ['leurs', 'aînées'], ['le', 'même', 'registre'], ['*T*', 'triptyque'], ['qui'], ['le', 'fronton'], ['la', 'république']]
        # DONE FINISH THIS METHOD!
        assert self.bnp_marked == False

        # These two numbers will be useful to see if all Minimal NPs found in PTBs
        # are marked.
        ph_count = len(phrases)
        ph_copy = phrases.copy()
        phw_count = sum(map(len, phrases))
        b_count = 0
        bw_count = 0
        pointer = 1

        while phrases:
            p = phrases.pop(0) # Current phrase
            lphrase = len(p)

            while pointer <= len(self.tokens)-lphrase:
                tokens_to_match = [] 
                for j in range(lphrase):
                    tokens_to_match.append(self.tokens[pointer+j])
                
                # This self._match() method will take care of matching.
                # If the phrases match, tokens will be marked BI,
                # if not, they are marked O.
                # The return avalue is either True or False, meaning if they are
                # matched successfully.
                if self._match(p, tokens_to_match):
                    # print('We have a match')
                    # print(p)
                    # print(tokens_to_match)
                    for i in range(len(tokens_to_match)):
                        # print(tokens_to_match[i].form)
                        if i == 0:
                            tokens_to_match[i].bnp = 'B'
                            b_count += 1
                            bw_count += 1
                        else:
                            tokens_to_match[i].bnp = 'I'
                            bw_count += 1
                    pointer += 1
                    break
                else:
                    pointer += 1

        for tok in self.tokens:
            if not self.tokens[tok].bnp:
                self.tokens[tok].bnp = 'O'

        self.bnp_marked = True

        if ph_count == b_count and phw_count == bw_count:
            return 'PERFECT! Total phrases: {}. Total words: {}.'.format(ph_count, phw_count)
        else:
            return 'XXXXXXX! Marked phrases: {}. Marked tokens: {}.\n{}'.format(b_count/(ph_count+0.0000001), bw_count/(phw_count+0.0000001), str(ph_copy))

    def output_ext_tree(self):
        """This method prints the dep tree with bnps
        marked in an extended conllu file."""
        # TODO In order to print exactly same trees
        # TODO Wait! How do they treat stuff like
        # y-a-t'il in the French UD?
        assert self.bnp_marked == True
        output = self.sentid_line+'\n'
        for tok in self.tokens.values():
            line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                tok.idx, tok.form, tok.lemma, tok.pos, tok.xpos, tok.feats, tok.head, tok.rel, tok.deps, tok.misc, tok.bnp
            )
            output += line
        output += '\n'
        return output

    def output_nnfeats(self, option, morph_feats = False):
        """Use command to output nn feats (labels are always output):
        - pos: Only the POS tag of each token,
        - pos_deprel: 1) the pos tag of each token,
                2) deprel with previous; and
                3) deprel with next token
        - pos_dep: 1) the pos tag of each token,
                2) if there is deprel with previous; and
                3) if there is deprel with next
        - pos_dep_parent: 1) POS of each token,
                2) deprel with its parent token,
                3) pos of its parent token
        - pos_dep_grand: 1) pos of each token, 2) deprel and 3) pos of its parent token;
                4) deprel and 5) pos of its grandparent token.
        - pos_parent: 1) POS of each token; and 2) POS of its parent.
        - pos_grand: 1) POS of each token, and POS of its 2) parent and 3) grandparent.
        - pos_parent_child: 1) POS of token; 2) of parent; and 3) of left-most child.
        - pos_dep_parent_child: 1) POS of token, 2) rel to parent, 3) POS of parent;
                4) rel from left-most child to current token; 5) POS of left-most child.
        """
        mapping = {'pos':self._feat_pos(mf=morph_feats), 'pos_deprel': self._feat_pos_deprel(mf=morph_feats), 'pos_dep':self._feat_pos_dep(mf=morph_feats), 'pos_dep_parent':self._feat_pos_dep_parent(mf=morph_feats), 'pos_dep_grand':self._feat_pos_dep_grand(mf=morph_feats), 'pos_parent':self._feat_pos_parent(mf=morph_feats), 'pos_grand':self._feat_pos_grand(mf=morph_feats), 'pos_parent_child':self._feat_pos_parent_child(mf=morph_feats), 'pos_dep_parent_child': self._feat_pos_dep_parent_child(mf=morph_feats)}
        assert option in mapping.keys()

        return mapping[option]

    def _feat_pos(self, mf):
        """Outputs:
            1) POS current token
        Or:
            1-9) POS plus a series of morph features of current token
        """
        output = ''
        for i in self.tokens:
            if not mf:
                line = '{}\t{}\n'.format(self.tokens[i].pos, self.tokens[i].bnp)
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8, self.tokens[i].bnp)
            output += line
        return output + '\n'

    def _feat_pos_dep(self, mf):
        """Outputs:
            1) POS of current token;
            2) relation with previous token, if it's head; 
            3) relation with next token, if it's head.
        If gn is turned on:
            1-9) POS, morph features of current token;
            10) True if the previous token is head, False if not; 
            11) True if the next token is head, False if not.
        """
        
        output = ''
        for i in self.tokens:
            previous_tok_is_head = ((i - self.tokens[i].head) == 1)
            next_tok_is_head = ((self.tokens[i].head - i) == 1)
            if not mf:
                line = '{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos,
                    previous_tok_is_head,
                    next_tok_is_head,
                    self.tokens[i].bnp
                )
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    previous_tok_is_head,
                    next_tok_is_head,
                    self.tokens[i].bnp
                )
            output += line
        
        return output + '\n'

    def _feat_pos_deprel(self, mf):

        """Outputs:
            1) POS of current token;
            2) relation with previous token, if it's head; 
            3) relation with next token, if it's head.
        If gn is turned on:
            1-9) POS, morph features of current token
            10) relation with previous token, if it's head; 
            11) relation with next token, if it's head.
        """
        
        output = ''
        for i in self.tokens:
            if (i - self.tokens[i].head) == 1:
                previous_tok_is_head = self.tokens[i].rel
            else:
                previous_tok_is_head = '_'
            
            if (self.tokens[i].head - i) == 1:
                next_tok_is_head = self.tokens[i].rel
            else:
                next_tok_is_head = '_'
            
            if not mf:
                line = '{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos,
                    previous_tok_is_head,
                    next_tok_is_head,
                    self.tokens[i].bnp
                )
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    previous_tok_is_head,
                    next_tok_is_head,
                    self.tokens[i].bnp
                )

            output += line
        return output +'\n'
    
    def _feat_pos_dep_parent(self, mf):
        """Outputs:
            1) POS; 2) rel to parent; 3) POS of parent.
        If gn turned on:
            1-9) POS, morph features of current token;
            10) rel to parent;
            11) POS of parent.
        """

        output = ''

        for i in self.tokens:
            if self.tokens[i].head:
                parent_pos = self.tokens[self.tokens[i].head].pos
            else:
                parent_pos = '_'

            if not mf:
                line = '{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos,
                    self.tokens[i].rel,
                    parent_pos,
                    self.tokens[i].bnp
                )
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                #       1   2   3   4   5   6   7   8   9   10  11  12
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    self.tokens[i].rel,
                    parent_pos,
                    self.tokens[i].bnp
                )
            output += line
        return output + '\n'
    
    def _feat_pos_dep_grand(self, mf):
        """Outputs:
            1) POS of current token; 2) rel from current to parent token; 3) parent POS;
            4) parent to grand rel; 5) grand pos.
        If gn turned on:
            1-9) POS and morph features of current token;
            10) rel from current to parent token;
            11) POS of parent token;
            12) rel from parent to grandparent token;
            14) POS, gender, number of grandparent token.
        """
        
        output = ''

        for i in self.tokens:
            p_idx = self.tokens[i].head

            if p_idx:
                parent_pos = self.tokens[p_idx].pos
                parent_to_grand_rel = self.tokens[p_idx].rel

                grand_idx = self.tokens[p_idx].head
                if grand_idx != 0:
                    grand_pos = self.tokens[grand_idx].pos
                else:
                    grand_pos = '_'
            else:
                parent_pos = '_'
                grand_pos = '_'
                parent_to_grand_rel = '_'

            if not mf:
                line = '{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos,
                    self.tokens[i].rel,
                    parent_pos,
                    parent_to_grand_rel,
                    grand_pos,
                    self.tokens[i].bnp
                )
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                #       1   2   3   4   5    6   7  8   9  10   11  12  13  14
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8, self.tokens[i].rel,
                    parent_pos, parent_to_grand_rel,
                    grand_pos,
                    self.tokens[i].bnp
                )
            output += line
        return output + '\n'

    def _feat_pos_parent(self, mf):
        """Outputs 1) POS tag, 2) parent POS tag.
        If gn turned on:
        1-9) POS morph features of current token; and
        10) POS of parent token."""

        output = ''

        for i in self.tokens:
            if self.tokens[i].head:
                parent_pos = self.tokens[self.tokens[i].head].pos
            else:
                parent_pos = '_'

            if not mf:                
                line = '{}\t{}\t{}\n'.format(
                    self.tokens[i].pos,
                    parent_pos,
                    self.tokens[i].bnp
                )
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                #        1  2   3   4   5   6   7   8   9   10  11
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    parent_pos,
                    self.tokens[i].bnp
                )

            output += line
        return output + '\n'

    def _feat_pos_grand(self, mf):
        """Outputs:
        1) POS of current token,
        2) of parent token,
        3 of grandparent token
        If gn turned on:
        1-9) POS and morph features of current  token
        10) POS of parent token; and
        11) POS of grandparent token.
        """

        output = ''

        for i in self.tokens:
            p_idx = self.tokens[i].head

            if p_idx:
                parent_pos = self.tokens[p_idx].pos
                grand_idx = self.tokens[p_idx].head
                if grand_idx != 0:
                    grand_pos = self.tokens[grand_idx].pos
                else:
                    grand_pos = '_'

            else:
                parent_pos = '_'
                grand_pos = '_'

            if not mf:
                line = '{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos,
                    parent_pos,
                    grand_pos,
                    self.tokens[i].bnp
                )
            else:
                f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
                #       1   2   3   4   5   6   7   8   9   10  11  12
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    self.tokens[i].pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    parent_pos,
                    grand_pos,
                    self.tokens[i].bnp
                )
            output += line
        return output + '\n'

    def _feat_pos_parent_child(self, mf):
        """Outputs in a file:
        1) POS of current token,
        2) POS of parent token,
        3) POS of leftmost child token, and
        4) POS of rightmost child token.
        Or: if gn == True:
        1-9) POS and morph features of current token; and
        10) POS of parent token; and
        11, 12) POS of leftmost and rightmost child token."""

        output = ''
        for i in self.tokens:
            this_pos = self.tokens[i].pos
            f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
            p_idx = self.tokens[i].head
            p_pos = self.tokens[p_idx].pos if p_idx else '_'
            # Getting the left most child is simple, it has min index value.
            # This is more or less an arbitrary decision.
            left_child_idx = min(self.children[i]) if self.children[i] else 0
            left_child_pos = self.tokens[left_child_idx].pos if left_child_idx else '_'

            right_child_idx = max(self.children[i]) if self.children[i] else 0
            if right_child_idx and right_child_idx != left_child_idx:
                right_child_pos = self.tokens[right_child_idx].pos
            else:
                right_child_pos = '_'

            if not mf:
                line = '{}\t{}\t{}\t{}\t{}\n'.format(
                    this_pos, p_pos, left_child_pos, right_child_pos, self.tokens[i].bnp
                )
            else:
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    this_pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    p_pos,
                    left_child_pos,
                    right_child_pos,
                    self.tokens[i].bnp
                )
            output += line

        return output +'\n'

    def _feat_pos_dep_parent_child(self, mf):
        """- pos_dep_parent_child:
            1) POS of token, 2) rel to parent, 3) POS of parent;
            4-5) POS of left-most child, rel from left-most child to current token; and
            6-7) POS of rightmost child, rel from rightmost child to current token.
        Or if gn is turn on:
            1-9) POS morph features of current token;
            10) deprel from current token to parent;
            11) POS of parent token;
            12-13) POS of leftmost child, leftmost-child-to-current deprel;
            14-15) POS of rightmost child, rightmost-child-to-current deprel."""

        output = ''
        
        for i in self.tokens:
            this_pos = self.tokens[i].pos
            this_dep = self.tokens[i].rel
            f1, f2, f3, f4, f5, f6, f7, f8 = self.tokens[i]._get_mf()
            p_idx = self.tokens[i].head
            p_pos = self.tokens[p_idx].pos if p_idx else '_'

            left_child_idx = min(self.children[i]) if self.children[i] else 0
            left_child_pos = self.tokens[left_child_idx].pos if left_child_idx else '_'
            left_child_dep = self.tokens[left_child_idx].rel if left_child_idx else '_'

            right_child_idx = max(self.children[i]) if self.children[i] else 0
            if right_child_idx and right_child_idx != left_child_idx:
                right_child_pos = self.tokens[right_child_idx].pos
                right_child_dep = self.tokens[right_child_idx].rel
            else:
                right_child_pos = '_'
                right_child_dep = '_'

            if not mf:
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    this_pos, this_dep, p_pos,
                    left_child_dep, left_child_pos,
                    right_child_dep, right_child_pos,
                    self.tokens[i].bnp
                )
            else:
                #        1  2   3   4   5    6   7   8   9  10  11  12  13  14  15  16
                line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    this_pos, f1, f2, f3, f4, f5, f6, f7, f8,
                    this_dep, p_pos,
                    left_child_dep, left_child_pos,
                    right_child_dep, right_child_pos,
                    self.tokens[i].bnp
                )

            output += line
        
        return output +'\n'

    def __repr__(self):
        repr = ''
        for i in self.tokens.values():
            repr += i.form
            repr += ' '
        return repr
