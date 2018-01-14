import numpy as np
import sys
import argparse
import os
import json
import re

featurePath = '/u/cs401/A1/feats/';
slangPath = '/u/cs401/Wordlists/Slang';

Windows = True
if Windows:
    slangPath = "G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\\Wordlists\\Slang"

# define the pronouns
firstPersonPronouns = ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours']
secondPersonPronouns = ['you', 'your', 'yours', 'u', 'ur', 'urs']
thirdPersonPronouns = ['he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their', 'theirs']

# define the slang
with open(slangPath, "r") as file:
    # load in the slang list and remove trailing whitespace
    slangList = file.read().split('\n')
    slangList = [slang for slang in slangList if slang]

pronounTypes = [firstPersonPronouns, secondPersonPronouns, thirdPersonPronouns]

def extract1( comment ):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features
    '''

    print('TODO')
    # TODO: your code here
    comment = ' ' + comment + ' '
    feats = np.zeros(30)

    # counting the pronouns
    for i, pronounType in enumerate(pronounTypes):
        for pronoun in pronounType:
            feats[i] += len(re.findall(' '+pronoun+'/', comment))

    # counting coordinating conjunctions, past-tense verbs and future-tense verbs
    feats[3] = len(re.findall('/CC ', comment))
    feats[4] = len(re.findall('/(VBD|VBN) ', comment))
    feats[5] = 0

    # counting commas and multi-character punctuation
    feats[6] = len(re.findall(' ,/', comment))
    feats[7] = len(re.findall(' \W{2,}/', comment))

    # counting the nouns
    feats[8] = len(re.findall('/(NN|NNS) ', comment))
    feats[9] = len(re.findall('/(NNP|NNPS) ', comment))

    # counting adverbs and wh- words
    feats[10] = len(re.findall('/(RB|RBR|RBS) ', comment))
    feats[11] = len(re.findall('/(WDT|WP|WP\$|WRB) ', comment))

    # counting slang acronyms
    for slangWord in slangList:
        feats[12] += len(re.findall(' '+slangWord+'/', comment))

    # Count the upper case
    feats[9] = len(re.findall(' [A-Z]{3,}/', comment))



def main( args ):

    # load the data and create the necessary arrays
    data = json.load(open(args.input))
    feats = np.zeros( (len(data), 173+1))

    # TODO: Iterate through comments in JSON file
    prev_cat = ''
    for i, comment in enumerate(data):

        # Extract the first 29 features
        feats[i, :29] = extract1(comment['body'])

       # when the category changes, reload new files
        if prev_cat != comment['cat']:
            prev_cat = comment['cat']

            # open the text file with category IDs
            idText = comment['cat'] + '_IDs.txt'
            with open(featurePath+idText, "r") as file:
                idList = file.read().split('.\n')

            # open the category numpy array
            idData = comment['cat'] + '_feats.dat.npy'
            catArray = np.load(featurePath+idData)

        # retrieve the index of the id in the text file
        idIndex = idList.index(comment['id'])

        # capture the 144 features in the category array
        startIndex = idIndex * 144
        feats[i,29:173] = catArray[startIndex:(startIndex+144)]

        # store the category
        feats[i, 173] = comment['cat']


    np.savez_compressed( args.output, feats)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()


    main(args)

