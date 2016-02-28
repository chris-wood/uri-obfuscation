import sys
import getopt
import os
import os.path
import numpy as np
from scipy.interpolate import UnivariateSpline
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


HASH16SIZE = 2
HASH32SIZE = 4
HASH48SIZE = 6
HASH64SIZE = 8
HASH128SIZE = 16
HASH160SIZE = 20
HASH256SIZE = 32

tlv = []
hash16 = []
hash32 = []
hash48 = []
hash64 = []
hash128 = []
hash160 = []
hash256 = []


def usage():
    print "python tlv_vs_obfuscate.py -i <inputPath>"


def main(argv):
    inputPath = ""
    try:
        opts, args = getopt.getopt(argv,"hi:", ["ipath="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-i", "--ipath"):
            inputPath = arg
        else:
            usage()
            sys.exit(2)

    if inputPath == "":
        print "Missing input path"
        usage()
        sys.exit(2)

    if os.path.isfile(inputPath):
        processFile(inputPath)
    else:
        for filePath in [os.path.join(inputPath, f) for f in
                         os.listdir(inputPath) if
                         os.path.isfile(os.path.join(inputPath, f))]:
            processFile(filePath)

    plotResults()


def processFile(filePath):
    print "Processing '" + filePath + "'..."
    with open(filePath, "r") as f:
        for line in f:
            name = line.split("/")

            # TLV encoding size.
            tlvEncodingSize = 0
            for component in name:
                # Each TLV component has 2 bytes for type and 2 bytes for length,
                # so 4 extra bytes in total
                tlvEncodingSize = len(component) + 4
            tlv.append(tlvEncodingSize)

            # 16-bit encoding size.
            hash16EncodingSize = (HASH16SIZE + 2) * len(name)
            hash16.append(hash16EncodingSize)

            # 32-bit encoding size.
            hash32EncodingSize = (HASH32SIZE + 2) * len(name)
            hash32.append(hash32EncodingSize)

            # 48-bit encoding size.
            hash48EncodingSize = (HASH48SIZE + 2) * len(name)
            hash48.append(hash48EncodingSize)

            # 64-bit encoding size.
            hash64EncodingSize = (HASH64SIZE + 2) * len(name)
            hash64.append(hash64EncodingSize)

            # 128-bit encoding size.
            hash128EncodingSize = (HASH128SIZE + 2) * len(name)
            hash128.append(hash128EncodingSize)

            # 160-bit encoding size.
            hash160EncodingSize = (HASH160SIZE + 2) * len(name)
            hash160.append(hash160EncodingSize)

            # 256-bit encoding size.
            hash256EncodingSize = (HASH256SIZE + 2) * len(name)
            hash256.append(hash256EncodingSize)


def plotResults():
    plt.hold(True)

    plot(tlv, "TLV format")
    plot(hash16, "16-bit format")
    plot(hash32, "32-bit format")
    plot(hash48, "48-bit format")
    plot(hash64, "64-bit format")
    plot(hash128, "128-bit format")
    plot(hash160, "160-bit format")
    plot(hash256, "256-bit format")

    # Set grid, axis labels, and legend.
    plt.grid(True)
    plt.xlabel("Name length (bytes)")
    plt.ylabel("Probability density function")
    plt.legend()

    # Save to file.
    pp = PdfPages("tlv_vs_obfuscate.pdf")
    plt.savefig(pp, format='pdf')
    pp.close()


def plot(sizes, legendText):
    n = (len(sizes) / 10) # number of bins
    p, x = np.histogram(sizes, bins=n)
    x = x[:-1] + (x[1] - x[0])/2   # convert bin edges to centers
    f = UnivariateSpline(x, p, s=n)
    plt.plot(x, f(x), label=legendText)


if __name__ == "__main__":
    main(sys.argv[1:])
