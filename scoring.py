import json

configurations = ['pos',
'pos_dep',
'pos_dep_grand',
'pos_dep_grand_morph',
'pos_dep_morph',
'pos_dep_parent',
'pos_dep_parent_child',
'pos_dep_parent_child_morph',
'pos_dep_parent_morph',
'pos_deprel',
'pos_deprel_morph',
'pos_grand',
'pos_grand_morph',
'pos_morph',
'pos_parent',
'pos_parent_child',
'pos_parent_child_morph',
'pos_parent_morph']

with open('Yen_gold.json', 'r') as engin:
    Yen_gold = json.load(engin)

with open('Xen_words.json', 'r') as enwin:
    Xen_words = json.load(enwin)

with open('Yfr_gold.json', 'r') as frgin:
    Yfr_gold = json.load(frgin)

with open('Xfr_words.json', 'r') as frwin:
    Xfr_words = json.load(frwin)

# Precision =
# Num of correctly tagged tokens as phrase type X [ct]
# -----------------------------------------------
#    Num of detected tokens as phrase type X [dt]
#
# 
# Recall =
# Num of correctly tagged tokens as phrase type X [ct]
# -----------------------------------------------
#     Num of of tokens as phrase type X [at]

for conf in configurations:

    with open(conf+'_en_pred.json', 'r') as en_pred_in:
        Yen_hat = json.load(en_pred_in)

        ct_en = 0 # Correctly tagged tokens as base NP
        dt_en = 0 # Detected tokens as base NP, could be correct or not.
        at_en = 0 # Total number of tokens as base NP.

        for gold, hat in zip(Yen_gold, Yen_hat):
            
            if gold and hat:
                print(''.join(gold))
                print(''.join(hat))

                for g, h in zip(gold, hat):
                    
                    if h == '_':
                        continue

                    if g in ['B', 'I']:
                        at_en += 1

                    if h in ['B', 'I']:
                        dt_en += 1

                        if g == h:
                            ct_en += 1

    with open(conf+'_fr_pred.json', 'r') as fr_pred_in:
        Yfr_hat = json.load(fr_pred_in)

        ct_fr = 0 # Correctly tagged tokens as base NP
        dt_fr = 0 # Detected tokens as base NP, could be correct or not.
        at_fr = 0 # Total number of tokens as base NP.

        for gold, hat in zip(Yfr_gold, Yfr_hat):
            print(''.join(gold))
            print(''.join(hat))
            
            if gold and hat:

                for g, h in zip(gold, hat):
                    
                    if h == '_':
                        continue

                    if g in ['B', 'I']:
                        at_fr += 1

                    if h in ['B', 'I']:
                        dt_fr += 1

                        if g == h:
                            ct_fr += 1
    
    p_en = ct_en/dt_en #english precision
    r_en = ct_en/at_en #english recall
    f1_en = 2*p_en*r_en/(p_en+r_en)
    p_fr = ct_fr/dt_fr #french precision
    r_fr = ct_fr/at_fr #french recall
    f1_fr = 2*p_fr*r_fr/(p_fr+r_fr)
    p_all = (ct_en+ct_fr)/(dt_en+dt_fr)
    r_all = (ct_en+ct_fr)/(at_en+at_fr)
    f1_all = 2*p_all*r_all/(p_all+r_all)

    with open(conf+'_precision_recall.csv', 'w') as fout:

        fout.write('conf, p_en, r_en, f1_en, p_fr, r_fr, f1_fr, p_all, r_all, f1_all\n')
        fout.write('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(
            conf, p_en, r_en, f1_en, p_fr, r_fr, f1_fr, p_all, r_all, f1_all
        ))
