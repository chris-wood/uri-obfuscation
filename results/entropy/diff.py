import os
import sys

base = {}
with open("OUT_plain_21.csv", "rb") as fh:
    for line in fh:
        data = line.strip().split(",")
        base[int(data[0])] = float(data[1])

delta = {}
for i in range(1, 21):
    fname = "cisco_uris_SHA256_%d_21_flatten.csv" % (i)
    with open(fname, "rb") as fh:
        for line in fh:
            if "time" in line:
                break
            data = line.strip().split(" ")
            if int(data[0]) == (i + 1):
                delta[int(data[0])] = float(data[1])
                break

#print base
#print ""
#print delta
delta[1] = base[1]

for b in base:
    #print b
    if b not in delta:
        print "WTF"
        sys.exit(-1)
    print "%d & %.3f \\\\" % (b, delta[b] - base[b])

print ""
print ""
print ""

conds = []
for b in delta:
    if b == 1:
        continue
    print "%d & %.3f \\\\" % (b, delta[b] - delta[b - 1])
    conds.append(delta[b] - delta[b - 1])

import statistics

print statistics.mean(conds)
print statistics.stdev(conds)
print statistics.variance(conds)