# UPOS mapping
# - Note the maximum index is 17 but the total number of categories is 18.
# - Underscore means both no POS and padding.
pos2idx = {'_': 0, 'ADJ': 1, 'ADV': 2, 'INTJ': 3, 'NOUN': 4, 'PROPN': 5, 'VERB': 6,
'ADP': 7, 'AUX': 8, 'CCONJ': 9, 'DET': 10, 'NUM': 11, 'PART': 12, 'PRON': 13,
'SCONJ': 14, 'PUNCT': 15, 'SYM': 16, 'X': 17}

# Deprels mapping
# - Since underscore means no relation at all, which is also the case for padding
# - Relations with subtypes are combined to the main type.
# - Note the maximum index is 37 but the total number of categories is 38.

rel2idx = {'_': 0, "nsubj": 1, "obj": 2, "iobj": 3, "csubj": 4, "ccomp": 5, "xcomp": 6, "obl": 7, 
"vocative": 8, "expl": 9, "dislocated": 10, "advcl": 11, "advmod": 12, "discourse":13, "aux":14,
"cop":15, "mark":16, "nmod":17, "appos":18, "nummod":19, "acl":20, "amod":21, "det":22, 
"clf":23, "case":24, "conj": 25, "cc":26, "fixed":27, "flat": 28, "compound":29, "list": 30,
"parataxis":31,	"orphan":32, "goeswith": 33, "reparandum": 34, "punct": 35,  "root": 36, "dep": 37}

# Morph features mapping
# - Which morph features do we adopt?
# - Which values are there for each morph feature?
# - For each morph feat, the value '_' means such feat is not specified/available. If a OOV value is found, use OOV.

definite2idx = {'_':0, 'Ind':1, '2':2, 'Def':3, 'Com':4, 'Cons':5, 'OOV':6}
gender2idx = {'_':0, 'Neut':1, 'Unsp':2, 'Com':3, 'Fem':4, 'Masc':5, 'OOV':6}
number2idx = {'_':0, 'Coll':1, 'Count':2, 'Sing':3, 'Dual':4, 'Pauc':5, 'Ptan':6, 'Unsp':7, 'Plur':8, 'Adnum':9, 'Assoc':10, 'OOV':11}
prontype2idx = {'_':0, 'Art':1, 'Coll':2, 'Ind':3, 'Add':4, 'Int':5, 'Dem':6, 'Neg':7, 'Ref':8, 'Contrastive':9, 'Exc':10, 'Qnt':11, 'Tot':12, 'Emp':13, 'Refl':14, 'Rel':15, 'Prs':16, 'Ord':17, 'Rcp':18, 'OOV':19}
person2idx = {'_':0, '4':1, '0':2, '2':3, 'Auto':4, '3':5, '1':6, 'OOV':7}
poss2idx = {'_':0, 'Yes':1, 'OOV':2}
numtype2idx = {'_':0, 'Coll':1, 'Sets':2, 'MultDist':3, 'Dist':4, 'Frac':5, 'Range':6, 'OrdMult':7, 'OrdinalSets':8, 'Mult':9, 'Card':10, 'Ord':11, 'OOV':12}
case2idx = {'_':0, 'Ade':1, 'Add':2, 'Gen':3, 'Sub':4, 'Obl':5, 'Comp':6, 'Ela':7, 'Abl':8, 'Ine':9, 'Lat':10, 'Car':11, 'Apr':12, 'Tem':13, 'All':14, 'Com':15, 'Loc':16, 'Par':17, 'Per':18, 'Dat':19, 'Erg':20, 'Mal':21, 'Tra':22, 'NomAcc':23, 'Equ':24, 'Cau':25, 'Nom':26, 'Voc':27, 'Con':28, 'Abs':29, 'Temp':30, 'Ess':31, 'Prl':32, 'Advb':33, 'Ter':34, 'Ben':35, 'Ill':36, 'Egr':37, 'Dis':38, 'Ins':39, 'Del':40, 'Cns':41, 'Acc':42, 'Sup':43, 'Abe':44, 'OOV':45}

# Boolean
bool2idx = {'True':1, 'False':0}

# Label mapping:
bio = {'B': 3, 'I': 2, 'O': 1, '_': 0} # Underscore means padding.
oib = {3: 'B', 2: 'I', 1: 'O', 0: '_'}

# Column to mapping, dict:
    #    d = feats_dict['Definite'] if 'Definite' in feats_dict else '_'
    #             g = feats_dict['Gender'] if 'Gender' in feats_dict else '_'
    #             n = feats_dict['Number'] if 'Number' in feats_dict else '_'
    #             pt = feats_dict['PronType'] if 'PronType' in feats_dict else '_'
    #             p  = feats_dict['Person'] if 'Person' in feats_dict else '_'
    #             ps = feats_dict['Poss'] if 'Poss' in feats_dict else '_'
    #             nt = feats_dict['NumType'] if 'NumType' in feats_dict else '_'
    #             c = feats_dict['Case'] if 'Case' in feats_dict else '_'

# definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx,

column2mapping = {
    'pos': [pos2idx],
    'pos_dep': [pos2idx, bool2idx, bool2idx],
    'pos_dep_grand': [pos2idx, rel2idx, pos2idx, rel2idx, pos2idx],
    'pos_dep_grand_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, rel2idx, pos2idx, rel2idx, pos2idx],
    'pos_dep_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, bool2idx, bool2idx],
    'pos_dep_parent': [pos2idx, rel2idx, pos2idx],
    'pos_dep_parent_child': [pos2idx, rel2idx, pos2idx, rel2idx, pos2idx, rel2idx, pos2idx],
    'pos_dep_parent_child_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, rel2idx, pos2idx, rel2idx, pos2idx, rel2idx, pos2idx],
    'pos_dep_parent_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, rel2idx, pos2idx],
    'pos_deprel': [pos2idx, rel2idx, rel2idx],
    'pos_deprel_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, rel2idx, rel2idx],
    'pos_grand': [pos2idx, pos2idx, pos2idx],
    'pos_grand_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, pos2idx, pos2idx],
    'pos_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx],
    'pos_parent': [pos2idx, pos2idx],
    'pos_parent_child': [pos2idx, pos2idx, pos2idx, pos2idx],
    'pos_parent_child_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, pos2idx, pos2idx, pos2idx],
    'pos_parent_morph': [pos2idx, definite2idx, gender2idx, number2idx, prontype2idx, person2idx, poss2idx, numtype2idx, case2idx, pos2idx]
}
