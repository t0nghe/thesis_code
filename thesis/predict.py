import os
from helpers import *
from keras.models import load_model
from conllu import Tree
import json

MODELSDIR = "enmodels/"
ENSECTION = "/Users/tonghe/PROG/ThesisRepositoryOfTW/data/english/"
FRSECTION = "/Users/tonghe/PROG/ThesisRepositoryOfTW/data/french/"
configurations = ['pos', 'pos_deprel', 'pos_dep', 'pos_dep_parent',
                  'pos_dep_grand', 'pos_parent', 'pos_grand', 'pos_parent_child',
                  'pos_dep_parent_child', 'pos_morph', 'pos_deprel_morph',
                  'pos_dep_morph', 'pos_dep_parent_morph', 'pos_dep_grand_morph',
                  'pos_parent_morph', 'pos_grand_morph', 'pos_parent_child_morph',
                  'pos_dep_parent_child_morph']

Xen_words = []
Yen_gold = []
Xfr_words = []
Yfr_gold = []
en_test_source = ENSECTION + 'original/testset.txt'
fr_test_source = FRSECTION + 'original/testset.txt'

with open(en_test_source, 'r') as enin:
    sents = enin.read().split('\n\n')
    for sent in sents:
        this_tree = Tree(sent, mnp_marked=True)
        Xen_words.append(this_tree.list_forms())
        Yen_gold.append(this_tree.list_bios())

with open(fr_test_source, 'r') as frin:
    sents = frin.read().split('\n\n')
    for sent in sents:
        this_tree = Tree(sent, mnp_marked=True)
        Xfr_words.append(this_tree.list_forms())
        Yfr_gold.append(this_tree.list_bios())

with open('Xen_words.json', 'w') as word_out:
    json.dump(Xen_words, word_out)

with open('Yen_gold.json', 'w') as yg_out:
    json.dump(Yen_gold, yg_out)

with open('Xfr_words.json', 'w') as frword_out:
    json.dump(Xfr_words, frword_out)

with open('Yfr_gold.json', 'w') as fryg_out:
    json.dump(Yfr_gold, fryg_out)

for CONF in configurations:

    model_file = MODELSDIR + CONF+'.model'
    this_model = load_model(model_file, custom_objects={'ignore_accuracy': ignore_accuracy})

    Xen_gold, _ = load_data_from_files(80, CONF, 'en', [-1])
    Yen_hat = np.argmax(this_model.predict(Xen_gold), axis=2)

    # for k in Y_hat:
    #     print(len(k))
    #     print(k)

    predictions = []
    for sent in Yen_hat:
        labels = [oib[pred] for pred in sent]
        predictions.append(labels)

    with open(CONF+'_en_pred.json', 'w') as en_pred_out:
        json.dump(predictions, en_pred_out)
    

    Xfr_gold, _ = load_data_from_files(80, CONF, 'fr', [-1])
    Yfr_hat = np.argmax(this_model.predict(Xfr_gold), axis=2)

    # for k in Y_hat:
    #     print(len(k))
    #     print(k)

    predictions = []
    for sent in Yfr_hat:
        labels = [oib[pred] for pred in sent]
        predictions.append(labels)

    with open(CONF+'_fr_pred.json', 'w') as fr_pred_out:
        json.dump(predictions, fr_pred_out)