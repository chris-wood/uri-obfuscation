import os
import sys

# TODO: build up the map

with open(sys.argv[1], "r") as f:
    pairs = map(lambda line: line.strip().split(","), f.readlines())
    for pair in pairs:
        namein = pair[0]
        nameout = pair[1]
