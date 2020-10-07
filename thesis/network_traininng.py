import numpy as np
import random
import matplotlib.pyplot as plt
import pickle
from keras.layers.embeddings import Embedding
from keras.layers.core import Activation, Dense, Dropout
from keras.layers.recurrent import GRU, LSTM
from keras.layers import Concatenate
from keras.layers import Input
from keras.layers.wrappers import Bidirectional
from keras.models import Model
from helpers import *

configurations = ['pos', 'pos_deprel', 'pos_dep', 'pos_dep_parent',
                  'pos_dep_grand', 'pos_parent', 'pos_grand', 'pos_parent_child',
                  'pos_dep_parent_child', 'pos_morph', 'pos_deprel_morph',
                  'pos_dep_morph', 'pos_dep_parent_morph', 'pos_dep_grand_morph',
                  'pos_parent_morph', 'pos_grand_morph', 'pos_parent_child_morph',
                  'pos_dep_parent_child_morph']

#### Parameters to change ####
LANG = 'en' # or 'fr' or 'both'
CONF = 'pos_dep' # This variable decides all mappings and lengths
OUTDIR = CONF+'/'
# Load ENDIR when testing and training on English
# Load FRDIR when testing and training on French
# Load both when testing and training on both
#### Parameters to change ####
MAXLEN = 80
BATCHSIZE = 50

# #### INPUT LAYER ####
# # That handles mutable number of columns of input data
mapping = column2mapping[CONF]

def init_model(RNN):

    #############################################################
    ##### INPUT LAYER CHNAGES WITH MODEL AND GOES WITH CONF #####
    input_pos1 = Input(shape=(MAXLEN,))
    input_dep1 = Input(shape=(MAXLEN,)) # If the current token is related to the previous/next token
    input_dep2 = Input(shape=(MAXLEN,))
    # input_def = Input(shape=(MAXLEN,))
    # input_gender = Input(shape=(MAXLEN,))
    # input_number = Input(shape=(MAXLEN,))
    # input_prontype = Input(shape=(MAXLEN,))
    # input_person = Input(shape=(MAXLEN,))
    # input_poss = Input(shape=(MAXLEN,))
    # input_numtype = Input(shape=(MAXLEN,))
    # input_case = Input(shape=(MAXLEN,))
    # input_pos2 = Input(shape=(MAXLEN,))
    # input_pos3 = Input(shape=(MAXLEN,))
    # input_pos4 = Input(shape=(MAXLEN,))

    INPUTS = [input_pos1, input_dep1, input_dep2]
    #         , input_def, input_gender, input_number,
    #           input_prontype, input_person, input_poss, input_numtype,
    #           input_case, input_pos2, input_pos3, input_pos4]

    EMBEDDINGS = [Embedding(18, 8)(input_pos1),
                Embedding(2, 2)(input_dep1),
                Embedding(2, 2)(input_dep2)]
    #              Embedding(7, 4)(input_def),
    #              Embedding(7, 4)(input_gender),
    #              Embedding(12, 4)(input_number),
    #              Embedding(20, 8)(input_prontype),
    #              Embedding(8, 4)(input_person),
    #              Embedding(3, 2)(input_poss),
    #              Embedding(13, 8)(input_numtype),
    #              Embedding(46, 8)(input_case),
    #              Embedding(18, 8)(input_pos2),
    #              Embedding(18, 8)(input_pos3),
    #              Embedding(18, 8)(input_pos4)]

    combined_inputs = Concatenate()(EMBEDDINGS)
    ################ END CONFIGURATION ###################
    ######################################################

    dense_in = Dense(16, activation='tanh')(combined_inputs)
    dropout_in = Dropout(0.2)(dense_in)
    if RNN == 'GRU':
        bilstm1 = Bidirectional(GRU(80, return_sequences=True))(dropout_in)
        bilstm2 = Bidirectional(GRU(80, return_sequences=True))(bilstm1)
    else:
        bilstm1 = Bidirectional(LSTM(80, return_sequences=True))(dropout_in)
        bilstm2 = Bidirectional(LSTM(80, return_sequences=True))(bilstm1)
    dropout_out = Dropout(0.2)(bilstm2)
    dense_out = Dense(16, activation='relu')(dropout_out)
    output = Dense(4, activation='softmax')(dense_out)

    model = Model(inputs=INPUTS, outputs=output)
    return model

for RNN in ['GRU', 'LTSM']:
    for EPOCHS in [50, 40, 30]: # Don't run more epochs. You are not competing against any body.
        TRAIN_FILES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        random.shuffle(TRAIN_FILES)
        v_file = TRAIN_FILES.pop()
        VALID_FILES = [v_file]
        X_train, Y_train = load_data_from_files(MAXLEN, CONF, LANG, TRAIN_FILES)
        X_valid, Y_valid = load_data_from_files(MAXLEN, CONF, LANG, VALID_FILES)

        this_model = init_model(RNN)
        MODEL_NAME = "{} {}_{} ep{} val{}".format(CONF, LANG, RNN, EPOCHS, v_file)

        with open(OUTDIR+MODEL_NAME+'_began.txt', 'w') as f_began:
            f_began.write('Yup. I began!')

        this_model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy', ignore_accuracy])
        hist = this_model.fit(x=X_train, y=Y_train, batch_size = BATCHSIZE, epochs=EPOCHS, validation_data=(X_valid, Y_valid))

        with open(OUTDIR+MODEL_NAME+' hist.pickle', 'wb') as hist_out:
            pickle.dump(hist.history, hist_out)
        with open(OUTDIR+MODEL_NAME+' acc.txt', 'w') as acc_out:
            acc_out.write('# ignore accuracy\n')
            acc_out.write(str(hist.history['ignore_accuracy'])+'\n')
            acc_out.write('# val_ignore_accuracy\n')
            acc_out.write(str(hist.history['val_ignore_accuracy'])+'\n')
            acc_out.write('# train loss\n')
            acc_out.write(str(hist.history['loss'])+'\n')
            acc_out.write('# val loss\n')
            acc_out.write(str(hist.history['val_loss'])+'\n')
        this_model.save(OUTDIR+MODEL_NAME+'.model')
