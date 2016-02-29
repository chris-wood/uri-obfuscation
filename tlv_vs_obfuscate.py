import sys
import getopt
import os
import os.path
import numpy as np
import statistics as stat
from scipy.interpolate import UnivariateSpline
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


HASH16SIZE = 2
HASH32SIZE = 4
HASH48SIZE = 6
HASH64SIZE = 8
HASH128SIZE = 16
HASH160SIZE = 20

tlv = []
hash16 = []
hash32 = []
hash48 = []
hash64 = []
hash128 = []
hash160 = []


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


def plotResults():
    plotPDF()
    plotMeanSTD()


def plotPDF():
    plt.hold(True)

    plot(tlv, "TLV format")
    plot(hash16, "16-bit format")
    plot(hash32, "32-bit format")
    plot(hash48, "48-bit format")
    plot(hash64, "64-bit format")
    plot(hash128, "128-bit format")
    plot(hash160, "160-bit format")

    # Set grid, axis labels, and legend.
    plt.grid(True)
    plt.xlabel("Name length (bytes)")
    plt.ylabel("Probability density function")
    plt.legend()

    # Save to file.
    pp = PdfPages("tlv_vs_obfuscate_PDF.pdf")
    plt.savefig(pp, format='pdf')
    pp.close()
    plt.cla()


def plotMeanSTD():
    width = 0.35
    xShift = -0.20
    mean = []
    meanDiff = []
    std = []

    # Calculate means.
    mean.append(stat.mean(tlv))
    mean.append(stat.mean(hash16))
    mean.append(stat.mean(hash32))
    mean.append(stat.mean(hash48))
    mean.append(stat.mean(hash64))
    mean.append(stat.mean(hash128))
    mean.append(stat.mean(hash160))

    # Calculate means difference.
    meanDiff.append(((mean[1] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[2] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[3] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[4] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[5] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[6] - mean[0]) / mean[0]) * 100)

    # Calculate STD.
    std.append(stat.stdev(tlv))
    std.append(stat.stdev(hash16))
    std.append(stat.stdev(hash32))
    std.append(stat.stdev(hash48))
    std.append(stat.stdev(hash64))
    std.append(stat.stdev(hash128))
    std.append(stat.stdev(hash160))

    # Plot name lengths.
    fig, ax = plt.subplots()
    ind = np.arange(len(mean))
    rects = ax.bar(ind + width, mean, width, color='#0072bd', yerr=std)

    # Add some text for labels, title and axes ticks.
    ax.grid(True)
    ax.set_ylabel('Name length (bytes)')
    ax.set_xticks(ind + (width * 1.5))
    ax.set_xticklabels(('TLV', '16-bit', '32-bit', '48-bit', '64-bit',
                        '128-bit', '160-bit'))
    autoLabel(ax, rects, 3, xShift)

    # Save to file.
    pp = PdfPages('tlv_vs_obfuscate_NameLengths.pdf')
    plt.savefig(pp, format='pdf')
    pp.close()
    plt.cla()

    # Plot name length difference.
    fig, ax = plt.subplots()
    ind = np.arange(len(meanDiff))
    rects = ax.bar(ind + width, meanDiff, width, color='#d95319')

    # Add some text for labels, title and axes ticks.
    ax.grid(True)
    ax.set_ylabel('Name length (bytes)')
    ax.set_xticks(ind + (width * 1.5))
    ax.set_xticklabels(('16-bit', '32-bit', '48-bit', '64-bit', '128-bit',
                        '160-bit'))
    autoLabel(ax, rects, 10, 0)

    # Save to file.
    pp = PdfPages('tlv_vs_obfuscate_NameLengthsDiff.pdf')
    plt.savefig(pp, format='pdf')
    pp.close()
    plt.cla()


def plot(sizes, legendText):
    n = (len(sizes) / 10) # number of bins
    p, x = np.histogram(sizes, bins=n)
    x = x[:-1] + (x[1] - x[0])/2   # convert bin edges to centers
    f = UnivariateSpline(x, p, s=n)
    plt.plot(x, f(x), label=legendText)


def autoLabel(ax, rects, heightDiff, xShift):
    # Attach some text labels.
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2. + xShift, height + heightDiff,
                '%d' % int(height),
                ha='center', va='bottom')

if __name__ == "__main__":
    main(sys.argv[1:])
