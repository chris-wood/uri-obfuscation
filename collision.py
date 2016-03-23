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
from pydht.local.memory import LocalMemoryDHT


### "HASH" FUNCTIONS TO TRY
# CRC16 (16 bits)
# CRC32 (32 bits)
# MurmurHash (32 bits)
# SipHash (64 bits)
# MurmurHash (128 bits)
# SHA1 (160 bits)


COMPONENT_LIMIT = 20
NUM_OF_HASHTABLES = 100
DHT_PATH = "dht_tmp/"

counters = []
hashUsed = ["CRC16", "CRC32", "MMH3", "SIPHASH", "MMH3_128", "SHA1"]
dhts = {
    "CRC16"    : [],
    "CRC32"    : [],
    "MMH3"     : [],
    "SIPHASH"  : [],
    "MMH3_128" : [],
    "SHA1"     : []
}
obfuscators = {
    "CRC16"    : obfuscate.ObfuscatorCRC16(),
    "CRC32"    : obfuscate.ObfuscatorCRC32(),
    "MMH3"     : obfuscate.ObfuscatorMMH3(),
    "SIPHASH"  : obfuscate.ObfuscatorSipHash(),
    "MMH3_128" : obfuscate.ObfuscatorMMH3_128(),
    "SHA1"     : obfuscate.ObfuscatorSHA1()
}
labels = {
    "CRC16"    : "CRC 16-bit",
    "CRC32"    : "CRC 32-bit",
    "MMH3"     : "MurmurHash 32-bit",
    "SIPHASH"  : "SipHash 64-bit",
    "MMH3_128" : "MurmurHash 128-bit",
    "SHA1"     : "SHA1 160-bit"
}


def usage():
    print "python collision.py -i <inputPath> -o <outputType> -p"
    print "                    -c <componentsLimit> -d <dhtType>"
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
    print "\t--d, --dtype <dhtType>"
    print "\t\tidentifies where the DHT is stored, either 'disk' or 'memory',"
    print "\t\tdefault is 'memory'."


def main(argv):
    global COMPONENT_LIMIT
    global start_time
    global counters

    start_time = time.time()

    inputPath = ""
    outputType = "plot"
    plot = False
    dhtType = "memory"
    try:
        opts, args = getopt.getopt(argv,"hi:o:pc:d:", ["help", "ipath=",
                                                       "otype=", "plot",
                                                       "climit=", "dtype"])
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
        else:
            usage()
            sys.exit(2)

    if inputPath == "":
        print "Missing input path."
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

    if dhtType not in ("disk", "memory"):
        print "DHT type must be either 'disk' or 'memory'."
        usage()
        sys.exit(2)

    # Prepare DHTs.
    if dhtType == "disk":
        if os.path.isdir(DHT_PATH):
            shutil.rmtree(DHT_PATH, ignore_errors=True)

    for i in range(0, COMPONENT_LIMIT):
        for key in hashUsed:
            if dhtType == "disk":
                dhts[key].append(LocalDiskDHT(obfuscators[key].size(),
                                              NUM_OF_HASHTABLES, DHT_PATH + "/" +
                                              key + "/" + str(i + 1)))
            elif dhtType == "memory":
                dhts[key].append(LocalMemoryDHT(obfuscators[key].size(),
                                                NUM_OF_HASHTABLES))

    # Initialize all counters to 0.
    counters = [0] * COMPONENT_LIMIT

    print "Processing input files..."
    if plot == False:
        if os.path.isfile(inputPath):
            processFile(inputPath)
        else:
            for filePath in [os.path.join(inputPath, f) for f in
                             os.listdir(inputPath) if
                             os.path.isfile(os.path.join(inputPath, f))]:
                processFile(filePath)

        outputResults(outputType)
        print("--- %s seconds ---" % (time.time() - start_time))
    else:
        plotResultsFromFile(inputPath)
        print("--- %s seconds ---" % (time.time() - start_time))

    # Cleaning up.
    if dhtType == "disk":
        shutil.rmtree(DHT_PATH, ignore_errors=True)


def processFile(filePath):
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
                for key in hashUsed:
                    dhts[key][i].insert(obfuscators[key].obfuscateDecimal(name))
    print("\t--- %s seconds ---" % (time.time() - start_time))


def outputResults(outputType):
    collisions = processResults()

    if outputType == "plot":
        plotResults(collisions)
    elif outputType == "text":
        saveResults(collisions)


def processResults():
    global start_time
    collisions = {}

    print "Processing results..."
    for i in range(0, COMPONENT_LIMIT):
        print "\t" + str(i + 1) + " component(s)..."
        if counters[i] == 0:
            continue

        for key in hashUsed:
            if key not in collisions:
                collisions[key] = []

            collisions[key].append(dhts[key][i].calculateCollision())

        print("\t--- %s seconds ---" % (time.time() - start_time))

    return collisions


def plotResults(collisions):
    print "Plotting collision results..."
    plt.hold(True)

    for key in hashUsed:
        plot(collisions[key], labels[key])

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
    pp = PdfPages("collision.pdf")
    plt.savefig(pp, format='pdf')
    pp.close()
    plt.cla()


def saveResults(collisions):
    if os.path.isdir("collision_output"):
        shutil.rmtree("collision_output", ignore_errors=True)
    os.makedirs("collision_output")

    print "Saving results in text format..."
    for key in hashUsed:
        print "\t./collision_output/" + key + ".out..."
        with open("collision_output/" + key + ".out", "w+") as outFile:
            pickle.dump(collisions[key], outFile)


def plotResultsFromFile(inputPath):
    collisions = {}

    print "Reading results stored in text format"
    for key in hashUsed:
        print "\t" + os.path.join(inputPath, key + ".out") + "..."
        with open(os.path.join(inputPath, key + ".out"), "r") as inFile:
            collisions[key] = pickle.load(inFile)

    plotResults(collisions)


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)


if __name__ == "__main__":
    main(sys.argv[1:])
