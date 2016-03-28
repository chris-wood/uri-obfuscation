from concurrent.futures import *
import itertools
import time
import thread
import sys
import csv
import numpy as np

def array_to_key(a, n):
    '''
    Turn a list of at least n components into a single element (key).
    '''
    return tuple(a[0:n])

def group_counts(result):
    '''
    Count the number each time each key occurs in the set.

    Return the total number of elements in the set
    '''
    groups = {}
    total = 0
    for item in result:
        groups[item] = 1 if item not in groups else groups[item] + 1
        total += 1
    return groups, total

def entropy_product(p):
    return p * np.log2(p) if p > 0 else 0

# A global reference to the matrix which stores our URI data in memory.
matrix = None

def compute_entropy(cmax):
    '''
    Compute the entropy based on the first cmax components in all URIs.
    '''
    global matrix

    rows = []
    for row in matrix:
        if len(row) >= cmax:
            rows.append(row)

    keys = map(lambda r : array_to_key(r, cmax), rows)
    group, count = group_counts(keys)
    jpmf = dict(map(lambda l : (l, float(group[l]) / count), group))
    entropy = sum(map(lambda key : entropy_product(jpmf[key]), jpmf)) * -1

    return (cmax, entropy)

def main(fname, num_cols):
    '''
    Compute the entropy over every URI combination sequence based on the URIs
    in the given file.

    fname = name of file that has the URIs.
    num_cols = number of columns to use when computing the entropy.
    '''
    global results
    global matrix

    with open(fname, "r") as f:
        matrix = map(lambda line: line.strip().split("/"), f.readlines())
        num_rows = len(matrix)

        start = time.time()
        with ProcessPoolExecutor(max_workers = 8) as executor:
            for (cmax, entropy) in executor.map(compute_entropy, range(1, num_cols + 1)):
                print cmax, entropy
        end = time.time()

        # for cmax in results:
            # print cmax, results[cmax]

        print "Total time: %f" % (end - start)
        print >> sys.stderr, "Total time: %f" % (end - start)

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
