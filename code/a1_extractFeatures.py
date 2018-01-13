import numpy as np
import sys
import argparse
import os
import json

featurePath = '/u/cs401/A1/feats/';

def extract1( comment ):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features
    '''
    print('TODO')
    # TODO: your code here

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

