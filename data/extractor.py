import os
import sys
import csv

base = sys.argv[1] # e.g., "cisco_uris"

algs = ["SIPHASH", "SHA256", "AESCBC"]
max_index = 21

full_data = {}
flat_data = {}

for alg in algs:
    full_data[alg] = []
    flat_data[alg] = []

    for i in range(1, max_index):
        fullname = "%s_%s_%d_%d.csv" % (base, alg, i, max_index)
        flatname = "%s_%s_%d_%d_flatten.csv" % (base, alg, i, max_index)

        full_data[alg].append([0.0] * (max_index))
        flat_data[alg].append([0.0] * (max_index))

        with open(fullname, 'r') as fh:
            for line in fh:
                if "time" not in line:
                    index, time = line.strip().split(" ")
                    full_data[alg][i - 1][int(index) - 1] = float(time)

        with open(flatname, 'r') as fh:
            for line in fh:
                if "time" not in line:
                    index, time = line.strip().split(" ")
                    flat_data[alg][i - 1][int(index) - 1] = float(time)

    # Dump the results to a CSV file
    full_out = "total/%s_%s.csv" % (base, alg)
    with open(full_out, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in full_data[alg]:
            writer.writerow(row)

    flat_out = "total/%s_%s_flatten.csv" % (base, alg)
    with open(flat_out, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in flat_data[alg]:
            writer.writerow(row)
