import sys
import argparse
import os
import json

import html
import re
import string

import spacy

# File Paths
indir = '/u/cs401/A1/data/'
stopWordPath = '/u/cs401/Wordlists/abbrev.english'
abbrevWordPath = '/u/cs401/Wordlists/StopWords'

# For testing on my local machine
Windows = False
if Windows:
    indir = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\\data\\';
    stopWordPath = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\Wordlists\\StopWords'
    abbrevWordPath = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\Wordlists\\abbrev.english'


# Open files outside of main functions for efficiency

# stop words file
with open(stopWordPath, "r") as file:
    stop_words = file.read().split('\n')


def preproc1(comment, steps=range(1, 5)):
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
        modComm = re.sub(
            r"(http|www)[a-zA-Z0-9/@.:?!=&%_;~#$'*+]+", '', modComm)

    # Remove all punctuation
    if 4 in steps:
        modComm = re.sub(r'[^\w\s]', '', modComm)

    # convert text to lower case
    if 5 in steps:
        modComm = modComm.lower()

    return modComm


def main(args):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            print("Processing " + fullFile)

            data = json.load(open(fullFile))

            # TODO: select appropriate args.max lines
            start = args.ID[0] % len(data)
            max_iters = 0

            # TODO: read those lines with something like `j = json.loads(line)`
            while max_iters < args.max:
                j = json.loads(data[start])

            # TODO: choose to retain fields from those lines that are relevant to you
                k = {key: j[key] for key in ['id', 'body']}

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
    parser.add_argument(
        "-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument(
        "--max", help="The maximum number of comments to read from each file", default=10000)
    args = parser.parse_args()

    if (args.max > 200272):
        print("Error: If you want to read more than 200,272 comments per file, you have to read them all.")
        sys.exit(1)

    main(args)
