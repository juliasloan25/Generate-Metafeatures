# FILE: gen-metafeatures.py
# AUTHOR: Julia Sloan
# DATE: July 2020


import pandas as pd
import numpy as np
from copy import deepcopy
import scipy.special as sp
import sys
import os

# determine the number of final metafeatures
# note num_cols = num features
def get_num_metas(num_cols, is_mul, is_div, is_add, is_sub):
    num_metas = 0
    if is_mul:
        num_metas += int(sp.comb(num_cols, 2) + num_cols)
    if is_div: # account for both num/dem combinations
        num_metas += 2 * int(sp.comb(num_cols, 2))
    if is_add:
        num_metas += int(sp.comb(num_cols, 2))
    if is_sub:
        num_metas += int(sp.comb(num_cols, 2))
    return num_metas


# adds the specified line to the beginning of the file
def prepend_line(file, line):
    dummy = file + '.dum'

    # open original file in read mode and dummy in write mode
    with open(file, 'r') as read_obj, open(dummy, 'w') as write_obj:
        # write line to dummy file
        write_obj.write(line + '\n')

        # add lines from original file to dummy
        for l in read_obj:
            write_obj.write(l)

    # remove original file
    os.remove(file)
    # rename dummy file as original file
    os.rename(dummy, file)


# generate .csv to output
def make_csv(res, col_names, csv_name):
    # convert 2D array to dataframe and add column titles
    final = pd.DataFrame(res, columns=col_names)
    # convert the result 2D array to a .csv file
    final.to_csv(csv_name, index=False)


# generate .in to output (first line with num samples and num features)
def make_in(res, in_name):
    # gen first line for .in file (num samples, num features)
    num_samples = np.shape(res)[0]
    num_feats_all = np.shape(res)[1]

    # save res as text file
    np.savetxt(in_name, res, delimiter="\t")

    # add first line (num samples, num features) to text file
    prepend_line(in_name, str(num_samples) + '\t' + str(num_feats_all))




# constant to be used as result of division by 0
BIG_M = int(sys.maxsize / 10**8)

# access command-line arguments (operations)
file = sys.argv[1]
ops = sys.argv[2:]

is_mul = 'mul' in ops
is_div = 'div' in ops
is_add = 'add' in ops
is_sub = 'sub' in ops

# get data from spreadsheet
df = pd.read_excel(file)

# create list of feature names, excluding the target (at column 0)
names = list(df.columns.values)
feat_names = names[1:]

# convert dataframe to nparray, isolate years from features
arr = df.to_numpy()

# get first column : the target values
target_vals = np.array([arr[:, 0]]).T

# get all features as a 2D np array
feats = arr[:, 1:]

# copy array of features to initialize result array
res = deepcopy(feats)
num_rows = np.shape(feats)[0]
num_cols = np.shape(feats)[1] - 1 # remove 1 because of target

# get number of metafeatures based on inputs
num_metas = get_num_metas(num_cols, is_mul, is_div, is_add, is_sub)

# initialize metafeatures np array
metas = np.zeros((num_rows, num_metas))

# go through all combos of columns, adding to the metafeatures array
i = 0
for c1 in range(num_cols):
    for c2 in range(c1, num_cols):
        if is_mul:
            names.append(str(feat_names[c1]) + "*" + str(feat_names[c2])) # generate metafeature names
            metas[:, i] = (feats[:, c1] * feats[:, c2]) # generate metafeature values
            i += 1

        if is_div:
            if not (c1 == c2): # exclude case where same features
                names.append(str(feat_names[c1]) + "/" + str(feat_names[c2])) # generate metafeature names
                if (np.all(feats[:, c2] != 0)):
                    metas[:, i] = (feats[:, c1] / feats[:, c2]) # generate metafeature values
                else: # handle division by 0
                    for row in range(num_rows):
                        if feats[row, c2] == 0: # division by 0 case
                            metas[row, i] = BIG_M
                        else: # no division by 0 for this element
                            metas[row, i] = (feats[row, c1] / feats[row, c2])
                i += 1

                names.append(str(feat_names[c2]) + "/" + str(feat_names[c1]))
                if (np.all(feats[:, c1] != 0)):
                    metas[:, i] = (feats[:, c2] / feats[:, c1])
                else: # handle division by 0
                    for row in range(num_rows):
                        if feats[row, c1] == 0: # division by 0 case
                            metas[row, i] = BIG_M
                        else: # no division by 0 for this element
                            metas[row, i] = (feats[row, c2] / feats[row, c1])
                i += 1

        if is_add:
            if not (c1 == c2):
                names.append(str(feat_names[c1]) + "+" + str(feat_names[c2])) # generate metafeature names
                metas[:, i] = (feats[:, c1] + feats[:, c2]) # generate metafeature values
                i += 1

        if is_sub:
            if not (c1 == c2):
                names.append(str(feat_names[c1]) + "-" + str(feat_names[c2])) # generate metafeature names
                metas[:, i] = (feats[:, c1] - feats[:, c2]) # generate metafeature values
                i += 1

# add target function back to first column of result
res = np.hstack((target_vals, res))

# add metafeatures to end of result array
res = np.hstack((res, metas))



# USAGE: use this function to produce .csv file with metafeatures
make_csv(res, names, file[:-5] + '-METAFEATURES.csv')

# USAGE: use this function to produce .in file with metafeatures
make_in(res, file[:-5] + "-METAFEATURES.in")

# output message to tell user program was successful
print("\nDone! Check directory of " + file + " for output")
