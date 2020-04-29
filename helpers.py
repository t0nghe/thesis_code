from keras.utils import to_categorical
from keras.preprocessing import sequence
from keras import backend as K
import numpy as np
from mappings import *
import os

def _make_array(sent, mapping):
    """
    sent: str. A sentence in its `NN input form`.
    conf: name of current configuration as listed in the above `configurations' list.
    """
    # This function takes in a single sentence, it seems

    # This if statement removes empty lines and comments in 
    lines = [l for l in sent.split('\n') if l and not l.startswith('#')]
    arr_height = len(lines)
    # Because in the NN input files, the leftmost line is BIO.
    #arr_width = len(lines[0].split('\t'))-1
    arr_width = len(mapping)

    # OK... X_arr and Y_arr are NP arrays...
    X_arr = np.zeros((arr_height, arr_width), dtype=int)
    # Y_arr = np.zeros((arr_height, 1), dtype=int)
    Y_list = []

    for i in range(arr_height):
        try:
            (*feats, label) = lines[i].split('\t')
        except:
            continue

        for j in range(len(feats)):
            this_feat = feats[j]
            if ':' in this_feat:
                this_feat = this_feat.split(':')[0]
            X_arr[i, j] = mapping[j][this_feat]

        # Code below handles labels
        # Y_arr[i, 0] = bio[label]
        Y_list.append(int(bio[label]))

    return (X_arr, Y_list)

def _pad_feats_seq(sent_feats, seq_len, num_columns):
    """sent_feats: a series of sentence features, output from _make_array().
    - Note _make_array() handles single sentences.
    columns: number of columns in sentence features
    seq_len: arbitrary number that indicates the max length of sequence"""
    # The trick for the two functions to work is:
    # __make_array() outputs one sentence
    # I suppose `sent_feats` in this function means a lot of sents with their feats.
    
    #print(sent_feats)
    seqs = []
    # print(num_columns)
    for i in range(0, num_columns):
        seq = []
        #print(i)
        for sent in sent_feats:
            #print(sent)
            #single_feat = sent[i]
            #single_feat = sent[,:,i]
            single_feat = sent[:,i]
            # print(single_feat)
            seq.append(single_feat)
        seqs.append(seq)
    
    # Why did I use yield earlier?
    # Confused.
    # print("Inside _pad_feats_seq. len(seqs)")
    # print(len(seqs))
    # print("seqs")
    # print(seqs)
    output = [sequence.pad_sequences(seq, maxlen = seq_len, padding='post') for seq in seqs]
    # print("Output from _pad_feats_seq. len(seqs)")
    # print(output)
    return output


def make_labels(labels, seq_len):
    """labels is an input list that contains Y_list from multiple sents.
    Note: _make_array() handles and outputs a single sent."""

    labels_seq = sequence.pad_sequences(labels, maxlen = seq_len, padding="post")
    return to_categorical(labels_seq, num_classes=len(bio), dtype='int32')


def ignore_accuracy(y_true, y_pred):
    """Using this function in compile:
    `model.compile(loss='binary_crossentropy',
                    optimizer='adam',
                    metrics=['accuracy',
                        ignore_accuracy])
    Since in this particular case, we only need to ignore 0,
    I figure we don't need to use the fancier version."""
    
    # Also, if loading models fail, try this:
    # model = load_model('mymodel.h5', custom_objects={'ignore_accuracy':ignore_accuracy})
    to_ignore = 0 # Ignore the correctly predicted paddings.
    y_true_class = K.argmax(y_true, axis=-1)
    y_pred_class = K.argmax(y_pred, axis=-1)

    ignore_mask = K.cast(K.not_equal(y_pred_class, to_ignore), 'int32')
    matches = K.cast(K.equal(y_true_class, y_pred_class), 'int32') * ignore_mask
    accuracy = K.sum(matches) / K.maximum(K.sum(ignore_mask), 1)
    return accuracy

def load_data_from_files(seq_len, conf, target_lang, files: list):
    """target_lang: 'en', 'fr', 'both'
    This function should output: X_seqs and Y_gold.
    Which can be used to train, or used to compare against Y_hat.
    files: a list of integers, ie indices of files to open;
        Use `-1' to indicate the test set."""

    mapping = column2mapping[conf]
    num_columns = len(mapping)
    ENDIR = '/Users/tonghe/PROG/ThesisRepositoryOfTW/data/english/'
    FRDIR = '/Users/tonghe/PROG/ThesisRepositoryOfTW/data/french/'

    if -1 in files:
        filenames = ['testset.txt']
    else:
        filenames = [str(i)+'.txt' for i in files]

    sents_to_load = []
    for fn in filenames:
        if target_lang == 'en' or target_lang == 'both':
            with open(ENDIR+conf+'/'+fn, 'r') as fin:
                ftext = fin.read()
                sents_to_load.extend(ftext.split('\n\n'))
        if target_lang == 'fr' or target_lang == 'both':
            with open(FRDIR+conf+'/'+fn, 'r') as fin:
                ftext = fin.read()
                sents_to_load.extend(ftext.split('\n\n'))

    X_cats = [] # X in integers representing categories
    Y_cats = [] # Y in integers representing categories
    for sent in sents_to_load:
        if sent:
            X_singleton, Y_singleton = _make_array(sent, mapping)
            X_cats.append(X_singleton)
            Y_cats.append(Y_singleton)
        else:
            continue
        
    # print('X_cats')
    # print(len(X_cats))
    # print(X_cats)
    #print('Y_cats') # Y is perf.
    # print(len(Y_cats))
    #print(Y_cats)

    # print("Now let's see X_seqs, output from _pad_feats_seq.")
    X_seqs = _pad_feats_seq(X_cats, seq_len, num_columns)

    # THIS PART IS PERF!
    #print("Let's see output from make_labels.")
    Y_seqs = make_labels(Y_cats, seq_len)
    #print(Y_seqs)

    return X_seqs, Y_seqs

#a, b = load_data_from_files(150, 'pos_dep_grand_morph', 'fr', [100])
