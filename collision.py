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
CRC16_SIZE = 16
CRC32_SIZE = 32
MURMUR32_SIZE = 32
SIP_SIZE = 64
MURMUR128_SIZE = 128
SHA1_SIZE = 160
NUM_OF_HASHTABLES = 100
DHT_PATH = "dht_tmp/"

dht_crc16 = []
dht_crc32 = []
dht_murmur32 = []
dht_sip = []
dht_murmur128 = []
dht_sha1 = []
counters = []

def usage():
    print "python collision.py -i <inputPath> -o <outputType> -p"
    print "                           -c <componentsLimit>"
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
        elif opt == "-p":
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
        dht_crc16.append(dht.DHT(CRC16_SIZE, NUM_OF_HASHTABLES,
                                 DHT_PATH + "/crc16/" + str(i + 1)))
        dht_crc32.append(dht.DHT(CRC32_SIZE, NUM_OF_HASHTABLES,
                                 DHT_PATH + "/crc32/" + str(i + 1)))
        dht_murmur32.append(dht.DHT(MURMUR32_SIZE, NUM_OF_HASHTABLES,
                                 DHT_PATH + "/murmur32/" + str(i + 1)))
        dht_sip.append(dht.DHT(SIP_SIZE, NUM_OF_HASHTABLES,
                                 DHT_PATH + "/sip/" + str(i + 1)))
        dht_murmur128.append(dht.DHT(MURMUR128_SIZE, NUM_OF_HASHTABLES,
                                 DHT_PATH + "/murmur128/" + str(i + 1)))
        dht_sha1.append(dht.DHT(SHA1_SIZE, NUM_OF_HASHTABLES,
                                 DHT_PATH + "/sha1/" + str(i + 1)))

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
                # CRC.
                dht_crc16[i].insert(crc16.crc16xmodem(name) & 0xFFFF)
                dht_crc32[i].insert(binascii.crc32(name) & 0xFFFFFFFF)

                # Murmur hash.
                dht_murmur32[i].insert(mmh3.hash(name) & 0xFFFFFFFF)
                dht_murmur128[i].insert(mmh3.hash128(name) &
                                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

                # Siphash.
                key = "0123456789ABCDEF"
                sip = siphash.SipHash_2_4(key)
                sip.update(name)
                dht_sip[i].insert(sip.hash() & 0xFFFFFFFFFFFFFFFF)

                # SHA1.
                m = hashlib.new("sha1")
                m.update(name)
                dht_sha1[i].insert(int(m.hexdigest(), 16))


def outputResults(outputType):
    crc16_collision, crc32_collision, murmur32_collision, sip_collision, \
        murmur128_collision, sha1_collision = processResults()

    if outputType == "plot":
        plotResults(crc16_collision, crc32_collision, murmur32_collision,
                    sip_collision, murmur128_collision, sha1_collision)
    elif outputType == "text":
        saveResults(crc16_collision, crc32_collision, murmur32_collision,
                    sip_collision, murmur128_collision, sha1_collision)


def processResults():
    crc16_collision = []
    crc32_collision = []
    murmur32_collision = []
    sip_collision = []
    murmur128_collision = []
    sha1_collision = []

    for i in range(0, COMPONENT_LIMIT):
        if counters[i] == 0:
            continue

        crc16_collision.append(countCollition(DHT_PATH + "/crc16/" +
                                              str(i + 1)) / float(counters[i]))
        crc32_collision.append(countCollition(DHT_PATH + "/crc32/" +
                                              str(i + 1)) / float(counters[i]))
        murmur32_collision.append(countCollition(DHT_PATH + "/murmur32/" +
                                                 str(i + 1)) /
                                  float(counters[i]))
        sip_collision.append(countCollition(DHT_PATH + "/sip/" +
                                            str(i + 1)) / float(counters[i]))
        murmur128_collision.append(countCollition(DHT_PATH + "/murmur128/" +
                                                  str(i + 1)) /
                                   float(counters[i]))
        sha1_collision.append(countCollition(DHT_PATH + "/sha1/" +
                                             str(i + 1)) / float(counters[i]))

    return (crc16_collision, crc32_collision, murmur32_collision, sip_collision,
            murmur128_collision, sha1_collision)


def countCollition(path):
    count = 0
    for filePath in [os.path.join(path, f) for f in
                     os.listdir(path) if
                     os.path.isfile(os.path.join(path, f))]:
        with open(filePath, "r") as inFile:
            for line in inFile:
                chunk = line.split(":")
                if int(chunk[1]) > 1:
                    count = count + int(chunk[1])

    return count


def plotResults(crc16_collision, crc32_collision, murmur32_collision,
                sip_collision, murmur128_collision, sha1_collision):
    print "Plotting collision results..."
    plt.hold(True)

    plot(crc16_collision, "CRC 16-bit")
    plot(crc32_collision, "CRC 32-bit")
    plot(murmur32_collision, "MurmurHash 32-bit")
    plot(sip_collision, "SipHash 64-bit")
    plot(murmur128_collision, "MurmurHash 128-bit")
    plot(sha1_collision, "SHA1 160-bit")

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


def saveResults(crc16_collision, crc32_collision, murmur32_collision,
                sip_collision, murmur128_collision, sha1_collision):
    if os.path.isdir("collision_output"):
        shutil.rmtree("collision_output", ignore_errors=True)
    os.makedirs("collision_output")

    print "Saving results in text format..."
    print "\t./collision_output/crc16.out..."
    with open("collision_output/crc16.out", "w+") as outFile:
        pickle.dump(crc16_collision, outFile)

    print "\t./collision_output/crc32.out..."
    with open("collision_output/crc32.out", "w+") as outFile:
        pickle.dump(crc32_collision, outFile)

    print "\t./collision_output/murmur32.out..."
    with open("collision_output/murmur32.out", "w+") as outFile:
        pickle.dump(murmur32_collision, outFile)

    print "\t./collision_output/sip.out..."
    with open("collision_output/sip.out", "w+") as outFile:
        pickle.dump(sip_collision, outFile)

    print "\t./collision_output/murmur128.out..."
    with open("collision_output/murmur128.out", "w+") as outFile:
        pickle.dump(murmur128_collision, outFile)

    print "\t./collision_output/sha1.out..."
    with open("collision_output/sha1.out", "w+") as outFile:
        pickle.dump(sha1_collision, outFile)


def plotResultsFromFile(inputPath):
    print "Reading results stored in text format"
    print "\t" + os.path.join(inputPath, "crc16.out") + "..."
    with open(os.path.join(inputPath, "crc16.out"), "r") as inFile:
        crc16_collision = pickle.load(inFile)

    print "\t" + os.path.join(inputPath, "crc32.out") + "..."
    with open(os.path.join(inputPath, "crc32.out"), "r") as inFile:
        crc32_collision = pickle.load(inFile)

    print "\t" + os.path.join(inputPath, "murmur32.out") + "..."
    with open(os.path.join(inputPath, "murmur32.out"), "r") as inFile:
        murmur32_collision = pickle.load(inFile)

    print "\t" + os.path.join(inputPath, "sip.out") + "..."
    with open(os.path.join(inputPath, "sip.out"), "r") as inFile:
        sip_collision = pickle.load(inFile)

    print "\t" + os.path.join(inputPath, "murmur128.out") + "..."
    with open(os.path.join(inputPath, "murmur128.out"), "r") as inFile:
        murmur128_collision = pickle.load(inFile)

    print "\t" + os.path.join(inputPath, "sha1.out") + "..."
    with open(os.path.join(inputPath, "sha1.out"), "r") as inFile:
        sha1_collision = pickle.load(inFile)

    plotResults(crc16_collision, crc32_collision, murmur32_collision,
                sip_collision, murmur128_collision, sha1_collision)


if __name__ == "__main__":
    main(sys.argv[1:])
