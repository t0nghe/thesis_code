# Profile

My name is Tonghe Wang. I obtained MA in Computational Linguistics/Language Technology at Uppsala University, Sweden in 2020. This is a profile that reflects my academic achievement and my learning track.

## Learning Projects

My personal learning projects are shared in the [learning](https://github.com/t0nghe/learning) repository. Specifically, I learn about algorithms and data structures by solving LeetCode challenges in Python and JavaScript. I learn JavaScript-based web development following the *[Full Stack Open](https://fullstackopen.com/en/)* online course given by Helsinki University. I read *[Hands-On Machine Learning 2](https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/)* to better understand machine learning and deep learning techniques. These are long-term projects and I'll tackle them step by step.

## Courses I Took

*Course name (credits, grade)*

* Programming for Language Technologists (7.5, VG) and Advanced Programming for Language Technologists (7.5, VG)
* Master's Thesis (30, VG)
* Artificial Intelligence (5, 4)
* Current Topics in Digital Philology (5, G)
* Information Retrieval (7.5, G)
* Language Technology: R&D (15, G)
* Machine Learning in NLP (7.5, G)
* Machine Translation (5, G)
* Mathematics for Language Technologists (7.5, G)
* Natural Language Processing (15, G)
* Syntactic Parsing (7.5, G)

## Assignments and Projects

**Master's Thesis**

In my [master's thesis](https://www.diva-portal.org/smash/record.jsf?pid=diva2%3A1438674&dswid=-1934), I used a Bi-LSTM architecture to tag noun phrases in Universal Dependencies corpora. Python scripts used for pre-processing the data and training the network are shared in my [thesis_code](/thesis) repository. A `readme` file is added to explain how each component works.

**Implementing Earley parser**

In this assignment in the Syntactic Parsing course, I implemented the Earley algorithm for constituency parsing. [earley_train.py](assignments/earley_train.py) and [earley_parse.py](assignments/earley_parse.py) are respectively the training and parsing components of the parser. 

The training component `earley_train.py` uses annotated syntactic trees as training data. From such training data, it learns production rules from the tree structure, terminals such as POS tags, and a vocabulary of most frequent words. The parsing component `earley_parse.py` uses the learned information to parse input sentences using the Earley algorithm. At each turn, it iterates through all states in the chart. This process is compounded by the fact that the Earley algorithm runs on cubic time when parsing.

**Crawling and indexing a website and comparing with Google**

This is an assignment for the Information Retrieval course. In [ir_crawl.py](assignments/ir_crawl.py) I scraped the official website of Uppsala kommun. The scraping process started from the homepage, unvisited pages were pushed to a stack and were ranked according to the number of incoming links. All scraped pages were converted to TREC foramt and were index using document retrieval engine [Indri](https://lemur.sourceforge.io/indri/). To compare the effectiveness of this index, measures such as P@10 (precision at 10), MAP (mean average precision) and DCG@10 (discounted cumulative gain at 10) were calculated on several query terms.

**Scraping Wikipedia** 

This is an assignment in the Advanced Programming course. In [prog_scraping.py](assignments/prog_scraping.py), I used `urllib` to fetch webpages from Wikipedia; `BeautifulSoup` to navigate DOM on a page.
