import os
import sys
import csv

min_key = 100000 # something big
with open(sys.argv[1], 'r') as infh:
    fnames = infh.readlines()
    names = []
    data = {}
    for fname in fnames:
        fname = fname.strip()
        with open(fname, 'r') as fh:
            names.append(fname.strip())
            for line in fh:
                line = line.strip().split(",")
                key = int(line[0])
                if key not in data:
                    data[key] = []
                data[key].append(float("{0:.3f}".format(float(line[1]))))

                if key < min_key:
                    min_key = key
print names
print data

with open(sys.argv[1] + ".joint.csv", 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    names = [""] + names
    writer.writerow(names)
    for key in data:
        line = [key] + data[key]
        writer.writerow(line)

with open(sys.argv[1] + ".cond.csv", 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    names = [""] + names
    writer.writerow(names)
    for key in data:
        if key == min_key:
            continue
        line = [key] + map(lambda v : float("{0:.3f}".format(v)), map(lambda (f, p): f - p, zip(data[key], data[key - 1])))
        writer.writerow(line)
