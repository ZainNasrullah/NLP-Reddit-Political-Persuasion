import sys
import argparse
import os
import json

import html
import re
import string

import spacy

# File Paths
indir = '/u/cs401/A1/data/';
stopWordPath = '/u/cs401/Wordlists/abbrev.english';
abbrevWordPath = '/u/cs401/Wordlists/StopWords';

# For testing on my local machine
Windows = True
if Windows:
    indir = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\\data\\';
    stopWordPath = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\Wordlists\\StopWords'
    abbrevWordPath = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\Wordlists\\abbrev.english'


# Open files outside of main functions for efficiency

# abbreviations file
with open(abbrevWordPath, "r") as file:
    abbrevs = file.read().split('.\n')
abbrevs_look = [r'(?<!\b' + a + r'\b)' for a in abbrevs]
abbrevs_regex = ''.join(abbrevs_look[:-1])

# stop words file
with open(stopWordPath, "r") as file:
    stop_words = file.read().split('\n')

# pre-load spacy
nlp = spacy.load('en', disable=['parser', 'ner'])

def preproc1( comment , steps=range(1,11)):
    ''' This function pre-processes a single comment

    Parameters:
        comment : string, the body of a comment
        steps   : list of ints, each entry in this list corresponds to a preprocessing step

    Returns:
        modComm : string, the modified comment
    '''
    modComm = comment

    # step 1: simple string replacement of all new line characters by a blank
    if 1 in steps:
        modComm = modComm.replace('\n', ' ')


    # step 2: convert all html tags to unicode using the html parser
    if 2 in steps:
        modComm = html.unescape(modComm)


    # step 3: remove all urls starting with http or www
    # somewhat deals with punctuation within URL but not fully
    if 3 in steps:
        modComm = re.sub(r"(http|www)[a-zA-Z0-9/@.:?!=&%_;~#$'*+]+", '', modComm)


    # step 4: add white space to around punctuation w/ exceptions
    if 4 in steps:
        modComm = re.sub(abbrevs_regex + "(\W?\.\W*)", r' \1 ', modComm)

        # replace all punctuation but periods, also handle special abbreviations like e.g.
        modComm = re.sub(r"\s?([^\w.\s'\-]+|(\w\.\w\.))\s?", r" \1 ", modComm)

        # remove any trailing double spaces that may have resulted above
        modComm = re.sub('\s{2,}', r' ', modComm)


    # step 5: separate into clitics
    if 5 in steps:
        # deals with possessives and common clitic forms
        modComm = re.sub(r"(\w)('(\W|s|ve|re|m|ll))", r'\1 \2', modComm)

        # case where a letter prior to the ' needs to join the second term
        modComm = re.sub(r"(\w)('t)", r' \1\2', modComm)


    # step 6: tokenize string and add tags
    if 6 in steps:
        # split string into tokens and tag using spacy
        tokens = modComm.split()
        doc = spacy.tokens.Doc(nlp.vocab, words=tokens)
        doc = nlp.tagger(doc)

        # rejoin tagged form of tokens
        modComm = ''
        for token in doc:
            modComm += token.text + '/' + token.tag_ + ' '
        modComm = modComm[:-1] # delete trailing space at end


    # step 7: remove stop words
    if 7 in steps:
        # split string into tokens
        tokenList = modComm.split()
        modList = []

        # split the text and tags
        for token in tokenList:
            if '/' in token:
                word_tag = token.split('/')
            else:
                word_tag = [token]

            # if the token not in stop words then add to modList
            if word_tag[0].lower() not in stop_words:
                modList.append(token)

        # recreate string
        modComm = ' '.join(modList)


    # step 8: replace tokens with lemmas except if lemma starts with a dash
    if 8 in steps:
        # check to see if step 6 occurred; if not, create tokens
        if 6 not in steps:
            tokens = modComm.split()
            doc = spacy.tokens.Doc(nlp.vocab, words=tokens)
            doc = nlp.tagger(doc)

        # add trailing spaces before and after string
        modComm = " " + modComm + " "

        # replace every token by its lemma
        for token in doc:
            if token.lemma_[0] != '-':
                # the additional space mitigates accidentally replacing words embedded in one another
                modComm = modComm.replace(r" "+token.text, r" " + token.lemma_)


    # step 9: find end of lines and deal with abbreviations
    # requires punctuation and tagged text
    if 9 in steps:
        # add end of line characters after end of line punctuation if string is tagged
        modComm = re.sub(r'([?!.]+"?/\.)', r'\1\n', modComm)

        if 6 not in steps:
        # add end of line characters after end of line punctuation if string is not tagged
            modComm = re.sub(abbrevs_regex + r'([?!.]+"?) ([A-Z])', r'\1\n\2', modComm)


    # convert text to lower case
    if 10 in steps:
        modComm = modComm.lower()

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
                print(max_iters)

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

