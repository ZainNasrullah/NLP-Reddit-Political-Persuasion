import numpy as np
import sys
import argparse
import os
import json

import re
import csv

featurePath = '/u/cs401/A1/feats/';
slangPath = '/u/cs401/Wordlists/Slang';
bnglPath = '/u/cs401/Wordlists/BristolNorms+GilhoolyLogie.csv'
warrPath = '/u/cs401/Wordlists/Ratings_Warriner_et_al.csv'

Windows = False
if Windows:
    slangPath = "G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\\Wordlists\\Slang"
    bnglPath = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\\Wordlists\\BristolNorms+GilhoolyLogie.csv'
    warrPath = "G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\\Wordlists\\Ratings_Warriner_et_al.csv"

# define the pronouns
firstPersonPronouns = ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours']
secondPersonPronouns = ['you', 'your', 'yours', 'u', 'ur', 'urs']
thirdPersonPronouns = ['he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their', 'theirs']
pronounTypes = [firstPersonPronouns, secondPersonPronouns, thirdPersonPronouns]

# define the slang
with open(slangPath, "r") as file:
    # load in the slang list and remove trailing whitespace
    slangList = file.read().split('\n')
    slangList = [slang for slang in slangList if slang]

# define bngl scores as two dimensional dictionary
with open(bnglPath) as csvfile:
    csvreader = csv.reader(csvfile)
    bngl_scores = {}

    next(csvreader) # skip header
    for row in csvreader:
        if row[1]: # avoid empty rows
            bngl_scores[row[1]]={'AoA':float(row[3]),'IMG':float(row[4]),'FAM':float(row[5])}

 # define warringer scores as two dimensional dictionary
with open(warrPath) as csvfile:
    csvreader = csv.reader(csvfile)
    warr_scores = {}

    next(csvreader) # skip header
    for row in csvreader:
        if row[1]: # avoid empty rows
            warr_scores[row[1]]={'V':float(row[2]),'A':float(row[5]),'D':float(row[8])}


def extract1( comment ):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 29-length vector of floating point features
    '''
    feats = np.zeros(29)

    # Add trailing spaces to comment if not already in place
    if comment[0] != ' ':
        comment = ' ' + comment

    if comment[-1] != ' ':
        comment = comment + ' '

    # counting the pronouns
    for i, pronounType in enumerate(pronounTypes):
        for pronoun in pronounType:
            feats[i] += len(re.findall(' '+pronoun+'/', comment))

    # counting coordinating conjunctions, past-tense verbs and future-tense verbs
    feats[3] = len(re.findall('/cc ', comment))
    feats[4] = len(re.findall('/(vbd|vbn) ', comment))
    feats[5] = 0

    # counting commas and multi-character punctuation
    feats[6] = len(re.findall(' ,/', comment))
    feats[7] = len(re.findall(' \W{2,}/', comment))

    # counting the nouns
    feats[8] = len(re.findall('/(nn|nns) ', comment))
    feats[9] = len(re.findall('/(nnp|nnps) ', comment))

    # counting adverbs and wh- words
    feats[10] = len(re.findall('/(rb|rbr|rbs) ', comment))
    feats[11] = len(re.findall('/(wdt|wp|wp\$|wrb) ', comment))

    # counting slang acronyms
    for slangWord in slangList:
        feats[12] += len(re.findall(' '+slangWord+'/', comment))

    # Count the upper case
    feats[13] = len(re.findall(' [A-Z]{3,}/', comment))

    # Split all sentences on the new line character
    sentences = re.findall('.*\n', comment)

    # count total sentence lengths in tokens and characters
    token_length = 0
    character_length = 0
    for sentence in sentences:

        # track number of tokens
        token_length += len(sentence.split())

        # for each token, if its not punctuation, add only the chars
        for token in sentence.split():
            word_token = re.search('(.*)/([a-zA-Z])', token)
            if word_token:
                character_length += len(word_token.group(1))

    # compute average sentence length in characters (excluding punctuation) and tokens
    feats[14] = token_length / len(sentences)
    feats[15] = character_length / len(sentences)
    feats[16] = len(sentences)

    # create lists to hold Bristol+GilhoolyLogie & Warringer scores
    AoA = []
    IMG = []
    FAM = []

    V = []
    A = []
    D = []

    # split comment into tokens, find the words and check to see if they exist in the bngl dictionary. If exist, add their score to the corresponding list
    comment_tokens = comment.split()
    for token in comment_tokens:
        text = re.search('(.*)/(.*)', token).group(1)

        if text in bngl_scores.keys():
            AoA.append(bngl_scores[text]['AoA'])
            IMG.append(bngl_scores[text]['IMG'])
            FAM.append(bngl_scores[text]['FAM'])

        if text in warr_scores.keys():
            V.append(warr_scores[text]['V'])
            A.append(warr_scores[text]['A'])
            D.append(warr_scores[text]['D'])

    # convert lists to numpy arrays
    AoAArray = np.array(AoA)
    IMGArray = np.array(IMG)
    FAMArray = np.array(FAM)

    VArray = np.array(V)
    AArray = np.array(A)
    DArray = np.array(D)

    # use numpy functions to find mean and standard deviations for scores
    feats[17] = AoAArray.mean()
    feats[18] = IMGArray.mean()
    feats[19] = FAMArray.mean()
    feats[20] = FAMArray.std()
    feats[21] = IMGArray.std()
    feats[22] = FAMArray.std()

    feats[23] = VArray.mean()
    feats[24] = AArray.mean()
    feats[25] = DArray.mean()
    feats[26] = VArray.std()
    feats[27] = AArray.std()
    feats[28] = DArray.std()

    return feats


def main( args ):

    # load the data and create the necessary arrays
    data = json.load(open(args.input))
    feats = np.zeros( (len(data), 173+1))

    category={'Left':0, 'Center':1, 'Right':2, 'Alt':3}

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
                idList = file.read().split('\n')

            # open the category numpy array
            idData = comment['cat'] + '_feats.dat.npy'
            catArray = np.load(featurePath+idData)

        # retrieve the index of the id in the text file
        idIndex = idList.index(comment['id'])

        # capture the 144 features in the category array
        feats[i,29:173] = catArray[idIndex, :]

        # store the category
        feats[i, 173] = category[comment['cat']]

        print(feats[i,:], feats.shape)
        input()

    np.savez_compressed( args.output, feats)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()


    main(args)

