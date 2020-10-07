# Documentation

## conllu.py

This file defines the `conllu.Tree` class. Internally, it maintains a dictionary of tokens, represented by the internal class named `Token`.

The `Token` class maintains properties for every column in the CoNLL-U format. In addition, it also maintains a property called `bnp` to reflect the 'BIO' markup.

The `conllu.Tree` class is initialized with a CoNLL-U tree represented in a string. With the `load_bnp` method, base NPs represented with lists of tokens are loaded. Then `Token` objects that are at the beginning, inside or outside of base NPs are respectively tagged.

With `output_ext_tree()` method, the dependency tree contained in this `conllu.Tree` object is output in the standard CoNLL-U format or in the extended format with 'BIO' labels.

The `output_nnfeats()} method outputs selected features to TSV files which is then used in the RNN.

## eng_bnp.py and fra_bnp.py

The functions `get_eng_bnp()` and `get_fra_bnp()` are respectively defined in these scripts. They load constituency trees in Penn-style bracketing and find base NPs in them. The output is a list containing lists of tokens, which can be passed to the `output_ext_tree()` method introduced in the above section.

## mappings.py

Mappings between keys and values are defined in this script. These mappings are used in pre- and post-processing of data for the RNN.

## helpers.py

This script helps the RNN run by loading data from files, padding and truncating sequences and transforming categorical data into arrays. The `ignore_accuracy()` function is defined in this script, which is used by Keras at compiling time to get real accuracies by excluding correctly predicted paddings.

## network_training.py

Variables `LANG` and `CONF` and the input layers defined in function `init_model()` vary between configurations to account for the different numbers of columns of input data.

For each configuration of input features, various models are defined and trained in the for-loop defined at the bottom.

## predict.py

This script is used at testing time. It loads the test set and iteratively makes predictions using trained models. Predictions are saved in `json} files for scoring.

## scoring.py

The predictions made by `predict.py` are compared against the labels of the test set. If the prediction (variable `hat`) and the label (variable `gold`) are the same, i.e. `B` for a `B` and `I` for an `I`, that prediction is counted as correct.