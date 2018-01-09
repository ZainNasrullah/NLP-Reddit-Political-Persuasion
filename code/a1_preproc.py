import sys
import argparse
import os
import json

import html
import re
import string


import spacy

indir = '/u/cs401/A1/data/';

def preproc1( comment , steps=range(1,11)):
    ''' This function pre-processes a single comment

    Parameters:                                                                      
        comment : string, the body of a comment
        steps   : list of ints, each entry in this list corresponds to a preprocessing step  

    Returns:
        modComm : string, the modified comment 
    '''

    modComm = comment
    nlp = spacy.load('en', disable=['parser', 'ner'])

    print(comment)

    if 1 in steps:
        modComm = modComm.replace('\n', '')

    print(modComm)

    if 2 in steps:
        modComm = html.unescape(modComm)

    if 3 in steps:
        modComm = re.sub(r'(http|www)\S+', '', modComm)

    print(modComm)

    if 4 in steps:
        # need to deal with more abbreviations
        modComm = re.sub(r"\s?([^\w\s'\-]+|(\w\.\w\.))\s?", r" \1 ", modComm)
        modComm = re.sub('\s{2,}', r'\s', modComm)

    # To do / fix
    if 5 in steps:
        while re.search(r"(\w+)('\w*)", modComm):
            p = re.search(r"(\w+)('\w*)", modComm)
            if p.group(2) == "'":
                pass
            elif p.group(2) == "'s" or  len(p.group(1)) == 1:
                modComm = modComm.replace(p.group(0), p.group(1) + ' ' + p.group(2))
            else:
                modComm = modComm.replace(p.group(0), p.group(1)[:-1] + ' ' + p.group(1)[-1] + p.group(2))


        modComm = re.sub('\s{2,}', r'\s', modComm)

    print(modComm)

    if 6 in steps:
        utt = nlp(modComm)
        modComm = ''
        # each punctuation treated as an independent token
        for token in utt:
            modComm += token.text + '/' + token.tag_ + ' '
        modComm = modComm[:-1]

    print(modComm)

    if 7 in steps:
        with open("/u/cs401/Wordlists/StopWords", "r") as file:
            stop_words = file.read().split('\n')
        tokenList = modComm.split()
        modList = []
        for token in tokenList:
            word_tag = token.split('/')
            if word_tag[0].lower() not in stop_words:
                modList.append(token)

        modComm = ' '.join(modList)

    print(modComm)

    # to do
    if 8 in steps:
        utt = nlp(modComm)
        for token in utt:
            if token.lemma_[0] != '-':
                modComm = modComm.replace(" "+token.text, " "+token.lemma_)

    print(modComm)

    if 9 in steps:
        pass

    if 10 in steps:
        modComm = modComm.lower()

    input()
        
    return modComm

def main( args ):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            print ("Processing " + fullFile)

            data = json.load(open(fullFile))

            # TODO: select appropriate args.max lines
            start = args.ID[0] % len(data)
            max_iters = 0

            #TODO: read those lines with something like `j = json.loads(line)`
            while max_iters < args.max:
                j = json.loads(data[start])
                
            # TODO: choose to retain fields from those lines that are relevant to you
                k = {key:j[key] for key in ['id', 'body']}

            # TODO: add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...) 
                k['cat'] = file
                
            # TODO: process the body field (j['body']) with preproc1(...) using default for `steps` argument
            # TODO: replace the 'body' field with the processed text
                k['body'] = preproc1(k['body'])

            
            # TODO: append the result to 'allOutput'
                allOutput.append(k)

                max_iters += 1
                start += 1
                if start == args.max:
                    start = 0

    fout = open(args.output, 'w')
    fout.write(json.dumps(allOutput))
    fout.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument('ID', metavar='N', type=int, nargs=1,
                        help='your student ID')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000)
    args = parser.parse_args()

    if (args.max > 200272):
        print ("Error: If you want to read more than 200,272 comments per file, you have to read them all.")
        sys.exit(1)

    main(args)
