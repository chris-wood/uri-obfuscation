import sys
from statistics import mean, median, stdev, variance

with open(sys.argv[1], "r") as fh:
    lines = []
    for line in fh:
        lines.append(line.strip())

    n = len(lines)

    print >> sys.stderr, "STATUS: Initializing namespace information..."

    byte_lengths = map(lambda n : len(n), lines)
    component_lengths = map(lambda n : len(n.split("/")), lines)
    max_name = reduce(lambda acc, n: acc if len(acc) > len(n.split("/")) else n, lines)
    components = map(lambda n : n.split("/"), lines)
    component_sizes = map(lambda ncl : map(lambda nc : len(nc), ncl), components)

    print >> sys.stderr, "\rSTATUS: Done collecting namespace information... Computing name-wise statistics."
    
    print "%f,%f,%f,%f" % (mean(byte_lengths), median(byte_lengths), stdev(byte_lengths), variance(byte_lengths))
    print >> sys.stderr, "\rSTATUS: Computing component-wise statistics"
    print "%f,%f,%f,%f" % (mean(component_lengths), median(component_lengths), stdev(component_lengths), variance(component_lengths))

    for i in range(0, len(max_name.split("/"))):
        print >> sys.stderr, "\rSTATUS: Computing component %d statistics" % (i)

        copy = filter(lambda n : len(n) > i, component_sizes)
        sample = map(lambda n : n[i], copy)
        print "%d,%f,%f,%f,%f" % (i, mean(sample), median(sample), stdev(sample), variance(sample))

