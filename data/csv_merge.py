import os
import sys
import csv

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
                data[key].append(line[1])

print names
print data

with open(sys.argv[1] + ".csv", 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    names = [""] + names
    writer.writerow(names)
    for key in data:
        line = [key] + data[key]
        writer.writerow(line)