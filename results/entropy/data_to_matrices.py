import os
import sys
import csv

algs = ["CRC16", "CRC32", "MMH3", "SHA256", "AESGCM", "AESCBC", "SIPHASH"]

prefix = sys.argv[1] # e.g., cisco_uris_
max_index = int(sys.argv[2])

def process_file(fname):
    data = []
    with open(fname, "r") as fh:
        for line in fh:
            if "time" in line:
                return data # end of line
            line = line.strip().split(" ")
            data.append(line[1])
    return data
 
# create the data matrices               
for alg in algs:
    flatten_data = []
    full_data = []
    data_set_prefix = "_".join([prefix, alg])
    for i in range(1, max_index):
        base = "_".join([prefix, alg, str(i), str(max_index)])

        flatten_name = base + "_flatten.csv"
        row = process_file(flatten_name)
        flatten_data.append(row)

        full_name = base + ".csv"
        row = process_file(full_name)
        full_data.append(row)        
        

    csvfile = data_set_prefix + "_flatten.csv"
    print >> sys.stderr, "Writing %s" % (csvfile)
    with open(csvfile, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in flatten_data:
            writer.writerow(row)

    csvfile = data_set_prefix + ".csv"
    print >> sys.stderr, "Writing %s" % (csvfile)
    with open(csvfile, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in full_data:
            writer.writerow(row)

    
        
            

            