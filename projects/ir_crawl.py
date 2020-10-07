# Code for a project in the Information Retrieval course as part
# of the Language Technology program at Uppsala University
# Tonghe Wang 2018

# This script scrapes the official website of Uppsala kommun
# and converts all pages as documents in TREC format.
# The downloaded pages are indexed using document retrieval engine Indri [https://lemur.sourceforge.io/indri/].
# The completeness of this index effort is later compared with Google on measures
# such as P@k (precision at k), MAP (mean average precision) and DCG@k (discounted cumulative gain at k).

import ssl
import sys
from urllib.parse import quote
import urllib.error
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import time

def parsePage(soup):
    '''Input: soup object for the entire HTML page.
    Output: Maintext from that HTML page, in a string.'''

    pageTitle = soup.find('title')
    pageTitle = pageTitle.get_text()
    pageText = ''

    if soup.find('div', class_='main-area') != None:
        mainSoup = soup.find('div', class_='main-area')
        mainTextList = mainSoup.get_text().split('\n')
        for line in mainTextList:
            line = line.strip()
            line = line.replace('\xa0', ' ')
            if line != 'Lyssna' and line != '' and line != 'Ja' and line != 'Nej':
                pageText += ('<P>' + line + '</P>\n')
    else:
        mainSoupList = soup.find_all('div', class_='container')
        for div in mainSoupList:
            mainTextList = div.get_text().split('\n')
            for line in mainTextList:
                line = line.strip()
                line = line.replace('\xa0', ' ')
                if line != 'Lyssna' and line != '' and line != 'Ja' and line != 'Nej':
                    pageText += ('<P>' + line + '</P>\n')
    
    return pageTitle, pageText

def outputTrec(title, permalink, fulltext, docno):
    # Input: title, page title; permalink, URL of the page, 
    # fulltext, main text of a webpage, docno, unique doc ID.
    doc = ''
    doc += '<DOC>\n'
    doc += '<DOCNO>{}</DOCNO>\n'.format(docno)
    doc += '<TITLE>{}</TITLE>\n'.format(title)
    doc += '<SOURCE>{}</SOURCE>\n'.format(permalink)
    doc += '<TEXT>{}</TEXT>\n'.format(fulltext)
    doc += '</DOC>\n\n'
    return doc

def get_page(to_visit, visited, docno):
    # Input: to_vist, a dictionary; visited, a list; docno, an int.
    # Output: to_vist; visited; docblock.
    # docblock contains the main text of a page.

    # Obtains one URL that has the most incoming links from dict to_visit.
    curmax = max(to_visit.values())
    i = list(to_visit.values()).index(curmax)
    permalink =  list(to_visit.keys())[i]
    print('Current: {}'.format(permalink))

    # The title, URL, and text will be saved in this docblock variable.
    # which will later be saved in a text file in TREC format.
    docblock = ''
    fullurl = None

    # Excludes pages that we do not want to collect.
    if ('.uppsala.se' in permalink) and ('readspeaker' not in permalink) \
    and ('BasePage/Cancel' not in permalink) and (':443' not in permalink) \
    and ('gamla-sidor' not in permalink) and ('https:' in permalink) \
    and (permalink not in visited) and ('bostad.uppsala.se/Image/' not in permalink) \
    and ('jsessionid' not in permalink) and ('Next/?year=' not in permalink):

        # If ssl verification doesn't work, which happens a lot, disables ssl verification.
        # Then if http error, very possibly 404, prompts page doesn't exist.
        try:
            time.sleep(0.300)
            mypage = urlopen(permalink)
        except urllib.error.URLError:
            try:
                no_verify = ssl._create_unverified_context()
                mypage = urlopen(permalink, context = no_verify)
            except:
                print('HTTP Error in reading {}.'.format(permalink))
                print('Will output an empty line.')
                visited.append(permalink)
                del to_visit[permalink]
                return to_visit, visited, docblock
        except UnicodeEncodeError:
            with open('unicode.txt', 'a') as errorlist:
                errorlist.write(permalink)
                errorlist.write('\n')
            
            visited.append(permalink)
            del to_visit[permalink]
            return to_visit, visited, docblock

        # The page content is held in this soup object
        soup = BeautifulSoup(mypage, "html.parser")

        # Made this set to avoid multiple occurances of the same URL.
        all_internal_links_on_this_page = set()

        print('#== Handling links')
        # This part deals with links
        for each_a in soup.find_all('a'):
            each_href = each_a.get('href')

            # These following links won't work.
            # So we'll skip them.
            if each_href == None or each_href == '':
                continue
            elif ('.zip' in each_href) or ('.png' in each_href) or \
                ('mailto:' in each_href) or ('tel:' in each_href) or \
                ('.doc' in each_href) or ('.pdf' in each_href) or \
                ('contentassets' in each_href) or ('docreader' in each_href) or \
                ('globalassets' in each_href):
                    continue

            parts_of_url = each_href.split('/')

            # If the href is a full url (that starts with http), then mark it as "to visit".
            # if 
            if 'http' in parts_of_url[0]:
                fullurl = each_href
                if '#' in fullurl:
                    fullurl = fullurl[:fullurl.index('#')]
            elif each_href[0] == '/':
                parts_of_perma = permalink.split('/')
                baseurl = parts_of_perma[0] + '/' + parts_of_perma[1] + '/' + parts_of_perma[2]
                parts_to_join = parts_of_url[:]
                parturl = '/'.join(parts_to_join)
                if parturl[0] == '/':
                    fullurl = baseurl + parturl
                else:
                    fullurl = baseurl + '/' + parturl
                if '#' in fullurl:
                    fullurl = fullurl[:fullurl.index('#')]
            
            if fullurl:
                all_internal_links_on_this_page.add(fullurl)

        for link in all_internal_links_on_this_page:
            if link not in visited:
                if link in to_visit.keys():
                    to_visit[link] += 1
                else:
                    to_visit[link] = 1

        # Parses the above soup and gets page title and fulltext.
        print('##= Parsing content.')
        try:
            title, fulltext = parsePage(soup)
        except:
            visited.append(permalink)
            del to_visit[permalink]
            return to_visit, visited, docblock

        print('### Writing Trec file.')
        docblock = outputTrec(title, permalink, fulltext, docno)

    visited.append(permalink)
    del to_visit[permalink]

    return to_visit, visited, docblock

# Main function
def main():

    # Batch number
    batch = '11A9'

    # Current page number in this batch
    counter = 1

    # This list contains lines to be written in a TREC file.
    trec_to_write = []

    # Tries to open to_visit.json and visited.json,
    # which contain links that remain to be fetched, 
    # and links that have been visited.
    with open('to_visit.json', 'r') as tv_json:
        to_visit = json.load(tv_json)
    with open('visited.json', 'r') as v_json:
        visited = json.load(v_json)

    # The number for counter controls batch size,
    # ie how many pages will be fetched 
    # and saved into a single TREC file.
    while counter <= 9999:

        # For the purpose of debugging.
        print('Handling batch {} page no. {}.'.format(batch, counter))

        docno = batch + str(counter).zfill(5)

        # See comment inside get_page function.
        (to_visit_after, visited_after, docblock) = get_page(to_visit, visited, docno)

        trec_to_write.append(docblock)

        # Write the content of webpage to a text file in TREC format.
        with open(batch + '.txt', 'w') as trec:
            trec.writelines(trec_to_write)

        print()
        counter += 1

    # When a batch is finished, save progress,
    # ie, webpages remain to be fetched and already visited,
    # respectively to json files.
    with open('to_visit.json', 'w') as tv_json:
        json.dump(to_visit_after, tv_json)
    with open('visited.json', 'w') as v_json:
        json.dump(visited_after, v_json)

def handleUnicode():

    batch = 'UNIC'
    counter = 1
    trec_to_write = []

    quoteurls = []
    with open('unicode.txt', 'r') as uni:
        longurls = uni.readlines()
        for url in longurls:
            stem = url[:url.index('=')]
            keyword = url[url.index('=')+1:]

            # The most important difference with main() is that
            # the part of URL that contains non-ASCII characters
            # is encoded by quote().
            newurl = stem + '=' + quote(keyword)
            quoteurls.append(newurl)
    
    for url in quoteurls:
        try:
            time.sleep(0.300)
            mypage = urlopen(url)
        except urllib.error.URLError:
            no_verify = ssl._create_unverified_context()
            mypage = urlopen(url, context = no_verify)
        
        soup = BeautifulSoup(mypage, "html.parser")

        (title, text) = parsePage(soup)
        print(url)
        print(title)

        docno = batch + str(counter).zfill(5)
        docblock = outputTrec(title, url, text, docno)
        trec_to_write.append(docblock)
        counter += 1

    with open(batch + '.txt', 'w') as trec:
        trec.writelines(trec_to_write)

# main()

# handleUnicode()