# Code for Assignment 3 in the Advanced Programming course at Uppsala University.
# Tonghe Wang & Hikaru Hashimoto, 2018
# This script queries a term in Wikipedia and prints out on screen a cleaned up plain text.

import ssl
import sys
from urllib.parse import quote
import urllib.error
from urllib.request import urlopen
from bs4 import BeautifulSoup

host = "https://en.wikipedia.org/wiki/"

# Accepts command line input and interactive input.
if len(sys.argv) >= 2:
    entry = '_'.join(sys.argv[1:])
elif len(sys.argv) < 2:
    entry = input('Type a term to look up: ')
    entryWords = entry.split(' ')
    entry = '_'.join(entryWords)

# Handles non-Ascii entry characters.
entry = quote(entry)
permalink = host + entry

# If ssl verification doesn't work, which happens a lot, disables ssl verification.
# Then if http error, very possibly 404, prompts page doesn't exist.
try:
    mypage = urlopen(permalink)
except urllib.error.URLError:
    try:
        no_verify = ssl._create_unverified_context()
        mypage = urlopen(permalink, context = no_verify)
    except urllib.error.HTTPError:
        print('Entry not found in Wikipedia.')
        exit()


# Gets the div that holds main content of the page.
soup = BeautifulSoup(mypage, "html.parser")
mydiv = soup.find('div', class_='mw-parser-output')

# This list is not necessary, just trying to have some control over print results.
to_print = []

for child in mydiv.children:

    # Tries to navigage through the main content and prints big chunks of text.
    if child.name in ['p', 'h2', 'h3', 'blockquote']:
        curLine = child.get_text()
        if child.name == 'p':
            to_print.append(curLine)
        elif child.name == 'h2':
            to_print.append('== '+curLine+' ==')
        elif child.name == 'blockquote':
            for grandchild in child.children:
                if grandchild.name in ['p', 'div']:
                    to_print.append('> ' + grandchild.get_text() )
        elif child.name == 'h3':
            to_print.append('= '+curLine+' =')

# Print out.
for p in to_print:
    if len(p) != 0:
        print(p)
        print()
