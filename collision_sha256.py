import getopt
import crc16
import binascii
import mmh3
import siphash
import hashlib
import sys
import time
import os
import os.path
import shutil
import pickle
import obfuscate
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from urlparse import urlparse
from pydht.local.disk import LocalDiskDHT
from pydht.local.db import LocalDbDHT
from pydht.local.memory import LocalMemoryDHT


COMPONENT_LIMIT = 20
NUM_OF_HASHTABLES = 100
DHT_PATH = "dht_tmp/"

counters = []
sizeUsed = ["16", "32", "48", "64", "128", "160"]
dhts = {
    "16"    : [],
    "32"    : [],
    "48"     : [],
    "64"  : [],
    "128" : [],
    "160"     : []
}
obfuscator = obfuscate.ObfuscatorSHA256()


def usage():
    print "python collision.py -i <inputPath> -o <outputType> -p"
    print "                    -c <componentsLimit> -d <dhtType>"
    print "                    -s <hashSize>"
    print ""
    print "\t-i, --iPath <inputPath>"
    print "\t\tis the path of a file containing the URI list, or a path to a"
    print "\t\tdirectory with a lot of files containing URI lists. If -p is"
    print "\t\tprovided, <inputPath> is the path of the output files to be"
    print "\t\tplotted."
    print "\t-o, --otype <outputType>"
    print "\t\tis optional and it is either 'text' or 'plot'. 'text' outputs the"
    print "\t\tgraphs in text format to be plotted later, while 'plot' (default)"
    print "\t\tplots the result."
    print "\t-p, --plot"
    print "\t\tis optional and if present, tlv_vs_obfuscate plots the text"
    print "\t\toutput provided in <inputPath> directory."
    print "\t-c, --climit <componentsLimit>"
    print "\t\tis the maximum number of components in a URI."
    print "\t-d, --dtype <dhtType>"
    print "\t\tidentifies where the DHT is stored, either 'disk', 'db' or"
    print "\t\t'memory'. Default is 'memory'."
    print "\t-s, --htype <hashSize>"
    print "\t\tis the size of the hash (obfuscation) function to use. Options:"
    print "\t\t'16', '32', '48', '64', '128', '160', or a comma separate list of"
    print "\t\tany of the previous values."


def main(argv):
    global COMPONENT_LIMIT
    global start_time
    global counters

    start_time = time.time()

    inputPath = ""
    outputType = "plot"
    plot = False
    dhtType = "memory"
    hashSize = ""
    try:
        opts, args = getopt.getopt(argv,"hi:o:pc:d:s:", ["help", "ipath=",
                                                         "otype=", "plot",
                                                         "climit=", "dtype",
                                                         "htype="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--ipath"):
            inputPath = arg
        elif opt in ("-o", "--otype"):
            outputType = arg
        elif opt in ("-p", "--plot"):
            plot = True
        elif opt in ("-c", "--climit"):
            COMPONENT_LIMIT = int(arg)
        elif opt in ("-d", "--dtype"):
            dhtType = arg
        elif opt in ("-s", "--htype"):
            hashSize = arg
        else:
            usage()
            sys.exit(2)

    if inputPath == "":
        print "Missing input path."
        usage()
        sys.exit(2)

    if hashSize == "":
        print "Missing hash size."
        usage()
        sys.exit(2)

    if outputType not in ("text", "plot"):
        print "Output type must be either 'text' or 'plot'."
        usage()
        sys.exit(2)

    if outputType == "text" and plot == True:
        print "Output type 'plot' cannot be use with -p."
        usage()
        sys.exit(2)

    if plot == True and os.path.isfile(inputPath):
        print "If -p is used, <inputPath> must be a directory."
        usage()
        sys.exit(2)

    if dhtType not in ("disk", "db", "memory"):
        print "DHT type must be either 'disk' or 'memory'."
        usage()
        sys.exit(2)

    sizes = []
    for size in hashSize.split(","):
        if not size in sizeUsed:
            print "Unknown hash size: '" + size + "'."
            usage()
            sys.exit(2)
        else:
            sizes.append(size)

    # Prepare DHTs.
    if dhtType == "disk":
        if os.path.isdir(DHT_PATH):
            shutil.rmtree(DHT_PATH, ignore_errors=True)

    for i in range(0, COMPONENT_LIMIT):
        for size in sizes:
            if dhtType == "disk":
                dhts[size].append(LocalDiskDHT(int(size), NUM_OF_HASHTABLES,
                                               DHT_PATH + "/" + size + "/" +
                                               str(i + 1)))
            elif dhtType == "db":
                dhts[size].append(LocalDbDHT(int(size), NUM_OF_HASHTABLES,
                                             DHT_PATH + "/" + size + "/" +
                                             str(i + 1)))
            elif dhtType == "memory":
                dhts[size].append(LocalMemoryDHT(int(size), NUM_OF_HASHTABLES))

    # Initialize all counters to 0.
    counters = [0] * COMPONENT_LIMIT

    print "Processing input files..."
    if plot == False:
        if os.path.isfile(inputPath):
            processFile(inputPath, sizes)
        else:
            for filePath in [os.path.join(inputPath, f) for f in
                             os.listdir(inputPath) if
                             os.path.isfile(os.path.join(inputPath, f))]:
                processFile(filePath, sizes)

        outputResults(outputType, sizes)
        print("--- %s seconds ---" % (time.time() - start_time))
    else:
        plotResultsFromFile(inputPath, sizes)
        print("--- %s seconds ---" % (time.time() - start_time))

    # Cleaning up.
    print "Cleaning up..."
    if dhtType in ("db"):
        for size in sizes:
            for i in range(0, COMPONENT_LIMIT):
                dhts[size][i].close()
    if dhtType in ("disk", "db"):
        shutil.rmtree(DHT_PATH, ignore_errors=True)
    print("--- %s seconds ---" % (time.time() - start_time))


def processFile(filePath, sizes):
    global start_time
    global counters

    print "\t'" + filePath + "'..."
    with open(filePath, "r") as inFile:
        for line in inFile:
            for i in range(0, COMPONENT_LIMIT):
                components = strip_scheme(
                    line.strip("\r").strip("\n")).split("/")

                if len(components) < i + 1:
                    continue

                counters[i] = counters[i] + 1

                name = "/" + "/".join(components[:i + 1])

                # Calculate hashes and insert them into the corresponding DHT.
                hashValue = obfuscator.obfuscate(name)
                for size in sizes:
                    dhts[size][i].insert(
                        int(hashValue[:((int(size) / 8) * 2)], 16))

    print("\t--- %s seconds ---" % (time.time() - start_time))


def outputResults(outputType, sizes):
    collisions = processResults(sizes)

    if outputType == "plot":
        plotResults(collisions, sizes)
    elif outputType == "text":
        saveResults(collisions, sizes)


def processResults(sizes):
    global start_time
    collisions = {}

    print "Processing results..."
    for i in range(0, COMPONENT_LIMIT):
        print "\t" + str(i + 1) + " component(s)..."
        if counters[i] == 0:
            continue

        for size in sizes:
            if size not in collisions:
                collisions[size] = []

            collisions[size].append(dhts[size][i].calculateCollision())

        print("\t--- %s seconds ---" % (time.time() - start_time))

    return collisions


def plotResults(collisions, sizes):
    print "Plotting collision results..."
    plt.hold(True)

    for size in sizes:
        plot(collisions[size], size + "-bit")

    finalizePlot()


def plot(prob, legendText):
    comps = range(1, len(prob) + 1)
    plt.plot(comps, prob, label=legendText)


def finalizePlot():
    # Set grid, axis labels, and legend.
    plt.grid(True)
    plt.xlabel("Number of name components")
    plt.ylabel("Collision probability")
    plt.legend()

    # Save to file.
    pp = PdfPages("collision_sha256.pdf")
    plt.savefig(pp, format='pdf')
    pp.close()
    plt.cla()


def saveResults(collisions, sizes):
    if os.path.isdir("collision_sha256_output"):
        if len(sizes) == len(sizeUsed):
            shutil.rmtree("collision_sha256_output", ignore_errors=True)
    else:
        os.makedirs("collision_sha256_output")

    print "Saving results in text format..."
    for size in sizes:
        print "\t./collision_sha256_output/" + size + ".out..."
        with open("collision_sha256_output/" + size + ".out", "w+") as outFile:
            pickle.dump(collisions[size], outFile)


def plotResultsFromFile(inputPath, sizes):
    collisions = {}

    print "Reading results stored in text format"
    for size in sizes:
        print "\t" + os.path.join(inputPath, size + ".out") + "..."
        with open(os.path.join(inputPath, size + ".out"), "r") as inFile:
            collisions[size] = pickle.load(inFile)

    plotResults(collisions, sizes)


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)


if __name__ == "__main__":
    main(sys.argv[1:])
