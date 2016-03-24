from concurrent.futures import *
import itertools
import time
import sys
import csv
import numpy as np

NUM_CORES = 8

def array_to_key(a, n):
    return tuple(a[0:n])

def group_counts(result):
    groups = {}
    total = 0
    for item in result:
        groups[item] = 1 if item not in groups else groups[item] + 1
        total += 1
    return groups, total

def entropy_product(p):
    return p * np.log2(p) if p > 0 else 0

def parallel_entropy(matrix, cmax):
    rows = []
    for row in matrix:
        if len(row) >= cmax:
            rows.append(row)
    with ThreadPoolExecutor(NUM_CORES) as executor:
        keys = list(executor.map(lambda r : array_to_key(r, cmax), rows))
        group, count = group_counts(keys)
        jpmf = dict(executor.map(lambda l : (l, float(group[l]) / count), group))
        entropy = sum(list(executor.map(lambda key : entropy_product(jpmf[key]), jpmf))) * -1
        return (cmax, entropy)

def sequential_entropy(matrix, cmax):
    rows = []
    for row in matrix:
        if len(row) >= cmax:
            rows.append(row)

    keys = list(map(lambda r : array_to_key(r, cmax), rows))
    group, count = group_counts(keys)
    jpmf = dict(map(lambda l : (l, float(group[l]) / count), group))
    entropy = sum(map(lambda key : entropy_product(jpmf[key]), jpmf)) * -1
    return (cmax, entropy)

# args[1] = input filename
# args[2] = max number of columns
def parallel(args):
    with open(args[1], "r") as f:
        matrix = map(lambda line: line.strip().split("/"), f.readlines())
        num_cols = int(args[2])
        num_rows = len(matrix)

        start = time.time()
        entropy_results = []
        with ThreadPoolExecutor(NUM_CORES) as executor:
            entropy_results = executor.map(lambda cols : parallel_entropy(matrix, cols), range(1, num_cols + 1))
        end = time.time()

        for (cmax, entropy) in entropy_results:
            print cmax, entropy

        print "Total time: %f" % (end - start)

def sequential(args):
    with open(args[1], "r") as f:
        matrix = map(lambda line: line.strip().split("/"), f.readlines())
        num_cols = int(args[2])
        num_rows = len(matrix)

        start = time.time()
        entropy_results = map(lambda cols : sequential_entropy(matrix, cols), range(1, num_cols + 1))
        end = time.time()

        for (cmax, entropy) in entropy_results:
            print cmax, entropy

        print "Total time: %f" % (end - start)

if __name__ == "__main__":
    if sys.argv[1] == "-p":
        parallel(sys.argv[1:])
    else:
        sequential(sys.argv[1:])
