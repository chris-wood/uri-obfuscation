import os
import sys
import math
import logging
import numpy as np
import itertools

import multiprocessing as mp
import itertools
import time
import csv

def entropy(jpmfs, *X):
    n_instances = len(X[0])
    H = 0
    for classes in itertools.product(*[set(x) for x in X]):
        # Only attempt to accumulate entropy bits if the combination is actually observed.
        found = False
        for i in range(len(jpmfs)):
            if classes in jpmfs[i]:
                found = True

        if found:
            v = np.array([True] * n_instances)
            for predictions, c in zip(X, classes):
                v = np.logical_and(v, predictions == c)
            p = np.mean(v)
            H += -p * np.log2(p) if p > 0 else 0
    return H

def fast_entropy(jpmfs, *X):
    n_instances = len(X[0])
    H = 0
    for key in jpmfs[-1]:
        classes = key
        v = np.array([True] * n_instances)
        for predictions, c in zip(X, classes):
            v = np.logical_and(v, predictions == c)
        p = np.mean(v)
        H += -p * np.log2(p) if p > 0 else 0
    return H

def conditional_entropy(jpmfs, Xs):
    if len(Xs) == 1:
        return fast_entropy(jpmfs, *Xs)
    else:
        full = fast_entropy(jpmfs, *Xs)
        partial = fast_entropy(jpmfs[0:len(jpmfs) - 1], *Xs[0:len(Xs)-1])
        return full - partial

def compute_joint_pmf(samples_list):
    '''
    Input: list of samples lists: [[sample-list-1], [sample-list-2], ...]
    Output: map from (symbol1, symbol2, ...) -> probability
    '''
    pmf = {}

    num_samples = min(reduce(lambda x, y: x + [len(y)], samples_list, []))
    num_lists = len(samples_list)
    for i in range(num_samples): # for each row
        symbols = []
        for j in range(num_lists): # for each col
            symbols.append(samples_list[j][i])

        key = tuple(symbols) # this is a key from a row "prefix"
        pmf[key] = 1 if key not in pmf else pmf[key] + 1

    total = num_samples
    for key in pmf:
        pmf[key] = pmf[key] / float(total)

    return pmf

def compute_distribution(pairs, cmin, cmax):
    if len(pairs) == 0:
        print cmin, cmax, "Can't compute the PMF of nothing!"
        return

    logging.debug("Starting run for cmin=%d cmax=%d" % (cmin, cmax))
    logging.debug("Pairs = %s" % (str(pairs)))

    # jpmfs holds the joint PMFs from cmin:cmin+1, cmin:cmin+2, ..., cmin:cmax
    # Each joint PMF is a map where keys are tuples and output is a probability (based on frequency of occurrence)
    jpmfs = []
    for i in range(cmin, cmax):
        jpmf = compute_joint_pmf(pairs[cmin:(i+1)])
        logging.debug(str(jpmf))
        jpmfs.append(jpmf)

    # Compute the joint and conditional entropy (they are not the same!)
    Hj = fast_entropy(jpmfs, *pairs[cmin:cmax])
    Hc = conditional_entropy(jpmfs, pairs[cmin:cmax])

    # Save the output
    print >> sys.stderr, ("%d,%d,%f,%f" % (cmin, cmax, Hj, Hc))
    print >> sys.stdout, ("%d,%d,%f,%f" % (cmin, cmax, Hj, Hc))

def main(args):
    logging.basicConfig(filename=args[1] + ".log", level=logging.DEBUG, format='%(message)s')

    with open(args[1], "r") as f:
        matrix = map(lambda line: line.strip()[1:].split("/"), f.readlines())
        num_cols = int(args[2]) # max number of components in a URI
        num_rows = len(matrix)

        # For each possible column slice
        for cmin in range(0, num_cols):
            for cmax in range(cmin + 1, num_cols + 1):
                # This will hold the columns of the matrix (the URI components)
                columns = []

                # For each column in the matrix
                for c in range(cmax):
                    column = map(lambda row : row[c], filter(lambda row : len(row) >= cmax, matrix))
                    columns.append(np.array(column))

                # Compute the distribution information from this column set (matrix)
                # The rows are the unique URIs
                # The columns are the column values of each URI
                # =>  row i, column j = j-th component of the i-th URI
                compute_distribution(columns, cmin, cmax)

if __name__ == "__main__":
    main(sys.argv)
