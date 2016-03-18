import getopt
import dht
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
    print "                    -c <componentsLimit>"
    print ""
    print "\t-i <inputPath>"
    print "\t\tis the path of a file containing the URI list, or a path to a"
    print "\t\tdirectory with a lot of files containing URI lists. If -p is"
    print "\t\tprovided, <inputPath> is the path of the output files to be"
    print "\t\tplotted."
    print "\t-o <outputType>"
    print "\t\tis optional and it is either 'text' or 'plot'. 'text' outputs the"
    print "\t\tgraphs in text format to be plotted later, while 'plot' (default)"
    print "\t\tplots the result."
    print "\t-p"
    print "\t\tis optional and if present, tlv_vs_obfuscate plots the text"
    print "\t\toutput provided in <inputPath> directory."
    print "\t-c"
    print "\t\tis the maximum number of components in a URI."


def main(argv):
    global start_time
    global counters

    start_time = time.time()

    inputPath = ""
    outputType = "plot"
    plot = False
    try:
        opts, args = getopt.getopt(argv,"hi:o:p", ["help", "ipath=", "otype=",
                                                   "plot"])
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
        else:
            usage()
            sys.exit(2)

    if inputPath == "":
        print "Missing input path."
        usage()
        sys.exit(2)

    if outputType == "text" and plot == True:
        print "Output type 'plot' cannot be use with -p."
        usage()
        sys.exit(2)

    # Prepare DHTs.
    if os.path.isdir(DHT_PATH):
        shutil.rmtree(DHT_PATH, ignore_errors=True)

    for i in range(0, COMPONENT_LIMIT):
        for key in hashUsed:
            dhts[key].append(dht.DHT(obfuscators[key].size(), NUM_OF_HASHTABLES,
                                     DHT_PATH + "/" + key + "/" + str(i + 1)))

    # Initialize all counters to 0.
    counters = [0] * COMPONENT_LIMIT

    if plot == False:
        if os.path.isfile(inputPath):
            processFile(inputPath)
            print("--- %s seconds ---" % (time.time() - start_time))
        else:
            for filePath in [os.path.join(inputPath, f) for f in
                             os.listdir(inputPath) if
                             os.path.isfile(os.path.join(inputPath, f))]:
                processFile(filePath)
            print("--- %s seconds ---" % (time.time() - start_time))

        outputResults(outputType)
        print("--- %s seconds ---" % (time.time() - start_time))
    else:
        plotResultsFromFile(inputPath)
        print("--- %s seconds ---" % (time.time() - start_time))

    # Cleaning up.
    shutil.rmtree(DHT_PATH, ignore_errors=True)


def processFile(filePath):
    global counters

    print "Processing '" + filePath + "'..."
    with open(filePath, "r") as inFile:
        for line in inFile:
            for i in range(0, COMPONENT_LIMIT):
                components = line.strip("http://").strip("https://").strip(
                    "ftp://").split("/")
                if len(components) < i + 1:
                    continue

                counters[i] = counters[i] + 1

                name = "/" + "/".join(components[:i + 1])

                # Calculate hashes and insert them into the corresponding DHT.
                for key in hashUsed:
                    dhts[key][i].insert(obfuscators[key].obfuscateDecimal(name))


def outputResults(outputType):
    collisions = processResults()

    if outputType == "plot":
        plotResults(collisions)
    elif outputType == "text":
        saveResults(collisions)


def processResults():
    collisions = {}

    for i in range(0, COMPONENT_LIMIT):
        if counters[i] == 0:
            continue

        for key in hashUsed:
            if key not in collisions:
                collisions[key] = []

            collisions[key].append(calculateCollision(DHT_PATH + "/" + key +
                                                      "/" + str(i + 1),
                                                      float(counters[i])))

    return collisions


def calculateCollision(path, total):
    count = 0
    for filePath in [os.path.join(path, f) for f in
                     os.listdir(path) if
                     os.path.isfile(os.path.join(path, f))]:
        with open(filePath, "r") as inFile:
            for line in inFile:
                chunk = line.split(":")
                if int(chunk[1]) > 1:
                    count = count + int(chunk[1])

    return count / float(total)


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


if __name__ == "__main__":
    main(sys.argv[1:])
