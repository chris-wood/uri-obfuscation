import os
import sys
import itertools
import matplotlib as m
import matplotlib.pyplot as plt
import Table

base_name = sys.argv[1]
base = {} # map from CMAX -> (Hj, Hc)
with open(base_name, "r") as fh:
    for line in fh:
        cmin, cmax, Hj, Hc = line.strip().split(",")
        if cmin == "0":
            base[cmax] = (Hj, Hc)

fname = sys.argv[2]
fhandle = open(fname, "r")

width = 1

joint_entropy = {}
conditional_entropy = {}
plotdata = []

maxcol = 0

# Colors are for each of the algorithms
# SIPHASH, CRC16, CRC32, AESGCM, AESCBC, MMH3, SHA256
colors = itertools.cycle(['red', 'black', 'blue', 'brown', 'green', 'yellow', 'orange'])

flat_data = {}
long_data = {}

def key_from_file(prefix, fname):
    name = fname[len(prefix) + 1:] # swallow the "_"
    data = name.split("_")
    alg = data[0]
    index = data[1][0:data[1].index(".")] if "." in data[1] else data[1]
    return alg, index

def append_flatten_data(key, cmin, cmax, Hj, Hc):
    flat_data[key].append((cmin, cmax, Hj, Hc))

def append_data(key, cmin, cmax, Hj, Hc):
    long_data[key].append((cmin, cmax, Hj, Hc))

with open(sys.argv[2], "r") as fh:
    for fname in fh:
        fname = fname.strip()
        flatten = "flatten" in fname
        key, index = key_from_file("big.txt", fname)

        if key not in flat_data:
            flat_data[key] = []
            long_data[key] = []

        with open(fname, "r") as handle:
            for line in handle:
                cmin, cmax, Hj, Hc = line.strip().split(",")
                if cmin == "0" and cmax == index:
                    if flatten:
                        append_flatten_data(key, cmin, cmax, Hj, Hc)
                    else:
                        append_data(key, cmin, cmax, Hj, Hc)                


# Create the table...
t = Table.Table(8, justs='lccccccc', caption='Table mang.', label="tab:table")
cols = [range(1, 21)] # base on the data
print len(flat_data.keys())
t.add_header_row(["Index Offset"] + flat_data.keys())

for key in flat_data:
    col = []
    for (cmin, cmax, Hj, Hc) in flat_data[key]:
        if int(cmax) < 21:
            orig = float(base[cmax][0])
            Hj = float(Hj)
            if orig == 0.0:
                col.append("NaN")
            else:
                percent = ((float(Hj) - float(orig)) / float(orig)) * 100.0
                col.append(percent)
            print cmin, cmax
    print len(col)
    cols.append(col)
    print len(col)
print cols
t.add_data(cols)
print len(cols)

t.print_table(sys.stdout)

