from concurrent.futures import *
import itertools
import time
import sys
import csv
import numpy as np

NUM_CORES = 8

def array_to_key(a, n):
    symbols = []
    for i in range(n):
        symbols.append(a[i])
    return tuple(symbols)

def single_count(l):
    return (l, 1)

def group_counts(result):
    groups = {}
    total = 0
    for item, count in result:
        groups[item] = 1 if item not in groups else groups[item] + 1
        total += count
    return groups, total

def reduce(l):
    return (l[0], sum(pair[1] for pair in l[1]))

def entropy_product(p):
    return p * np.log2(p) if p > 0 else 0

def compute_entropy(rows, cmax):
    with ThreadPoolExecutor(max_workers = NUM_CORES) as executor:
        print >> sys.stderr, "Create keys..."
        keys = list(executor.map(lambda r : array_to_key(r, cmax), rows))
        print >> sys.stderr, "Done."

        print >> sys.stderr, "Single count..."
        result = list(executor.map(single_count, keys))
        print >> sys.stderr, "Done."

        # TODO: this is a bottleneck.
        print >> sys.stderr, "Group counts..."
        group, count = group_counts(result)
        print >> sys.stderr, "Done"

        print >> sys.stderr, "Compute JPMF..."
        jpmf = dict(executor.map(lambda l : (l, float(group[l]) / count), group))
        print >> sys.stderr, "Done"

        print >> sys.stderr, "Compute entropy..."
        entropy = sum(list(executor.map(lambda key : entropy_product(jpmf[key]), jpmf))) * -1
        print >> sys.stderr, "Done."

        return entropy

# args[1] = input filename
# args[2] = output filename
def main(args):
    with open(args[1], "r") as f:
        matrix = map(lambda line: line.strip().split("/"), f.readlines())
        num_cols = int(args[2]) # max number of components in a URI
        num_rows = len(matrix)

        print >> sys.stderr, "Pulled the matrix into memory."

        for cmax in range(1, num_cols + 1):
            rows = []
            for row in matrix:
                if len(row) >= cmax:
                    rows.append(row)

            print >> sys.stderr, "Starting computation for CMAX=%d" % (cmax)
            entropy = compute_entropy(rows, cmax)
            print entropy

            with open(sys.argv[2], "w") as fout:
                writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([cmax, entropy])

if __name__ == "__main__":
    main(sys.argv)
