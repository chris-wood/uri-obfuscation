import os
import sys

def compute_pmf(pairs):
    pmf = {}
    for pair in pairs:
        pairin = pair[0]
        pairout = pair[1]
        key = (pairin, pairout)
        pmf[key] = 0 if key not in pmf else pmf[key] + 1
    return pmf

with open(sys.argv[1], "r") as f:
    pairs = map(lambda line: line.strip().split(","), f.readlines())
    compute_distribution(pairs)
