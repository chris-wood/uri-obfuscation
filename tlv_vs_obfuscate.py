import sys
import getopt
import os
import os.path
import shutil
import pickle
import time
import numpy as np
import statistics as stat
from scipy.interpolate import UnivariateSpline
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


OUTLIERS_LIMIT = 80
HASH16SIZE = 2
HASH32SIZE = 4
HASH48SIZE = 6
HASH64SIZE = 8
HASH128SIZE = 16
HASH160SIZE = 20

start_time = 0
tlv = []
hash16 = []
hash32 = []
hash48 = []
hash64 = []
hash128 = []
hash160 = []


def usage():
    print "python tlv_vs_obfuscate.py -i <inputPath> -o <outputType> -p -v"
    print "                           -o <errorType>"
    print ""
    print "\t-i <inputPath>"
    print "\t\tis the path of a file containing the URI list, or a path to a"
    print "\t\tdirectory with a lot of files containing URL lists. If -p is"
    print "\t\tprovided, <inputPath> is the path of the output files to be"
    print "\t\tplotted."
    print "\t-o <outputType>"
    print "\t\tis optional and it is either 'text' or 'plot'. 'text' outputs the"
    print "\t\tgraphs in text format to be plotted later, while 'plot' (default)"
    print "\t\tplots the result."
    print "\t-p"
    print "\t\tis optional and if present, tlv_vs_obfuscate plots the text"
    print "\t\toutput provided in <inputPath> directory."
    print "\t-v"
    print "\t\tis optional and only takes effect if the output type is 'text' or"
    print "\t\t-p is used. In this case, the output files will contain all"
    print "\t\tdistribution data. If this option is not provided (default),"
    print "\t\ttlv_cs_obfuscate will only saves the mean and standard deviation"
    print "\t\tof the results."
    print "\t-e"
    print "\t\tis the error type, either standard deviation 'stdev', minumum and"
    print "\t\tmaximum value 'yerr', or 'both'."


def main(argv):
    global start_time
    start_time = time.time()

    inputPath = ""
    outputType = "plot"
    plot = False
    verbose = False
    errorType = "both"
    try:
        opts, args = getopt.getopt(argv,"hi:o:pve:", ["ipath=", "otype=",
                                                      "etype="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-i", "--ipath"):
            inputPath = arg
        elif opt in ("-o", "--otype"):
            outputType = arg
        elif opt == "-p":
            plot = True
        elif opt == "-v":
            verbose = True
        elif opt in ("-e", "--etype"):
            errorType = arg
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

    if errorType not in ("stdev", "yerr", "both"):
        print "Error type must be either 'stdev', 'yerr', or 'both'."
        usage()
        sys.exit(2)

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

        plotResults(outputType, verbose, errorType)
        print("--- %s seconds ---" % (time.time() - start_time))
    else:
        plotResultsFromText(inputPath, verbose, errorType)
        print("--- %s seconds ---" % (time.time() - start_time))


def processFile(filePath):
    print "Processing '" + filePath + "'..."
    with open(filePath, "r") as inFile:
        for line in inFile:
            name = line.strip("http://").strip("https://").strip(
                "ftp://").split("/")

            # Skip all URIs with more than 80 name components, this gets rid of
            # outliers.
            if len(name) > OUTLIERS_LIMIT:
                continue

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


def plotResults(outputType, verbose, errorType):
    if outputType == "plot":
        if verbose:
            plotPDF()
        mean, meanDiff, std, min_yerr, max_yerr = calculateMeanErr(errorType)
        plotMeanErr(mean, meanDiff, std, min_yerr, max_yerr, errorType)
    elif outputType == "text":
        saveResults(verbose, errorType)


def plotResultsFromText(inputPath, verbose, errorType):
    if verbose:
        print "Reading verbose results in text format"
        print "\t" + os.path.join(inputPath, "tlv.out") + "..."
        with open(os.path.join(inputPath, "tlv.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        tlv.extend(tmp)

        print "\t" + os.path.join(inputPath, "hash16.out") + "..."
        with open(os.path.join(inputPath, "hash16.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        hash16.extend(tmp)

        print "\t" + os.path.join(inputPath, "hash32.out") + "..."
        with open(os.path.join(inputPath, "hash32.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        hash32.extend(tmp)

        print "\t" + os.path.join(inputPath, "hash48.out") + "..."
        with open(os.path.join(inputPath, "hash48.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        hash48.extend(tmp)

        print "\t" + os.path.join(inputPath, "hash64.out") + "..."
        with open(os.path.join(inputPath, "hash64.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        hash64.extend(tmp)

        print "\t" + os.path.join(inputPath, "hash128.out") + "..."
        with open(os.path.join(inputPath, "hash128.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        hash128.extend(tmp)

        print "\t" + os.path.join(inputPath, "hash160.out") + "..."
        with open(os.path.join(inputPath, "hash160.out"), "r") as inFile:
            tmp = pickle.load(inFile)
        hash160.extend(tmp)

        plotPDF()
        mean, meanDiff, std, min_yerr, max_yerr = calculateMeanErr(errorType)
    else:
        print "\t" + os.path.join(inputPath, "mean.out") + "..."
        with open(os.path.join(inputPath, "mean.out"), "r") as inFile:
            mean = pickle.load(inFile)

        print "\t" + os.path.join(inputPath, "meanDiff.out") + "..."
        with open(os.path.join(inputPath, "meanDiff.out"), "r") as inFile:
            meanDiff = pickle.load(inFile)

        std = []
        if errorType in ("stdev", "both"):
            print "\t" + os.path.join(inputPath, "std.out") + "..."
            with open(os.path.join(inputPath, "std.out"), "r") as inFile:
                tmp = pickle.load(inFile)
                std.extend(tmp)

        min_yerr = []
        max_yerr = []
        if errorType in ("yerr", "both"):
            print "\t" + os.path.join(inputPath, "min_yerr.out") + "..."
            with open(os.path.join(inputPath, "min_yerr.out"), "r") as inFile:
                tmp = pickle.load(inFile)
                min_yerr.extend(tmp)

            print "\t" + os.path.join(inputPath, "max_yerr.out") + "..."
            with open(os.path.join(inputPath, "max_yerr.out"), "r") as inFile:
                tmp = pickle.load(inFile)
                max_yerr.extend(tmp)

    plotMeanErr(mean, meanDiff, std, min_yerr, max_yerr, errorType)


def plotPDF():
    print "Plotting PDF..."
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


def plotMeanErr(mean, meanDiff, std, min_yerr, max_yerr, errorType):
    width = 0.35
    xShift = -0.20

    # Plot name lengths.
    print "Plotting name lengths..."

    if errorType in ("stdev", "both"):
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
        pp = PdfPages('tlv_vs_obfuscate_NameLengths_stdev.pdf')
        plt.savefig(pp, format='pdf')
        pp.close()
        plt.cla()

    if errorType in ("yerr", "both"):
        fig, ax = plt.subplots()
        ind = np.arange(len(mean))
        rects = ax.bar(ind + width, mean, width, color='#0072bd',
                       yerr=[min_yerr, max_yerr])

        # Add some text for labels, title and axes ticks.
        ax.grid(True)
        ax.set_ylabel('Name length (bytes)')
        ax.set_xticks(ind + (width * 1.5))
        ax.set_xticklabels(('TLV', '16-bit', '32-bit', '48-bit', '64-bit',
                            '128-bit', '160-bit'))
        autoLabel(ax, rects, 3, xShift)

        # Save to file.
        pp = PdfPages('tlv_vs_obfuscate_NameLengths_yerr.pdf')
        plt.savefig(pp, format='pdf')
        pp.close()
        plt.cla()

    # Plot name length difference.
    print "Plotting name length differences..."

    fig, ax = plt.subplots()
    ind = np.arange(len(meanDiff))
    rects = ax.bar(ind + width, meanDiff, width, color='#d95319')

    # Add some text for labels, title and axes ticks.
    ax.grid(True)
    ax.set_ylabel('Name length increment (%)')
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


def saveResults(verbose, errorType):
    global start_time

    if os.path.isdir("tlv_vs_obfuscate_output"):
        shutil.rmtree("tlv_vs_obfuscate_output", ignore_errors=True)
    os.makedirs("tlv_vs_obfuscate_output")

    if verbose:
        print "Saving verbose results in text format..."

        print "\t./tlv_vs_obfuscate_output/tlv.out..."
        with open("tlv_vs_obfuscate_output/tlv.out", "w+") as outFile:
            pickle.dump(tlv, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

        print "\t./tlv_vs_obfuscate_output/hash16.out..."
        with open("tlv_vs_obfuscate_output/hash16.out", "w+") as outFile:
            pickle.dump(hash16, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

        print "\t./tlv_vs_obfuscate_output/hash32.out..."
        with open("tlv_vs_obfuscate_output/hash32.out", "w+") as outFile:
            pickle.dump(hash32, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

        print "\t./tlv_vs_obfuscate_output/hash48.out..."
        with open("tlv_vs_obfuscate_output/hash48.out", "w+") as outFile:
            pickle.dump(hash48, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

        print "\t./tlv_vs_obfuscate_output/hash64.out..."
        with open("tlv_vs_obfuscate_output/hash64.out", "w+") as outFile:
            pickle.dump(hash64, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

        print "\t./tlv_vs_obfuscate_output/hash128.out..."
        with open("tlv_vs_obfuscate_output/hash128.out", "w+") as outFile:
            pickle.dump(hash128, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

        print "\t./tlv_vs_obfuscate_output/hash160.out..."
        with open("tlv_vs_obfuscate_output/hash160.out", "w+") as outFile:
            pickle.dump(hash160, outFile)
        print("\t--- %s seconds ---" % (time.time() - start_time))

    mean, meanDiff, std, min_yerr, max_yerr = calculateMeanErr(errorType)

    print "Saving non-verbose results in text format..."
    print "\t./tlv_vs_obfuscate_output/mean.out..."
    with open("tlv_vs_obfuscate_output/mean.out", "w+") as outFile:
        pickle.dump(mean, outFile)

    print "\t./tlv_vs_obfuscate_output/meanDiff.out..."
    with open("tlv_vs_obfuscate_output/meanDiff.out", "w+") as outFile:
        pickle.dump(meanDiff, outFile)

    if errorType in ("stdev", "both"):
        print "\t./tlv_vs_obfuscate_output/std.out..."
        with open("tlv_vs_obfuscate_output/std.out", "w+") as outFile:
            pickle.dump(std, outFile)

    if errorType in ("yerr", "both"):
        print "\t./tlv_vs_obfuscate_output/min_yerr.out..."
        with open("tlv_vs_obfuscate_output/min_yerr.out", "w+") as outFile:
            pickle.dump(min_yerr, outFile)

        print "\t./tlv_vs_obfuscate_output/max_yerr.out..."
        with open("tlv_vs_obfuscate_output/max_yerr.out", "w+") as outFile:
            pickle.dump(max_yerr, outFile)

    print("--- %s seconds ---" % (time.time() - start_time))


def calculateMeanErr(errorType):
    global start_time
    mean = []
    meanDiff = []
    std = []
    min_yerr = []
    max_yerr = []

    # Calculate means.
    print "Calculating means..."
    print "\tTLV mean..."
    mean.append(stat.mean(tlv))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 16-bit mean..."
    mean.append(stat.mean(hash16))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 32-bit mean..."
    mean.append(stat.mean(hash32))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 48-bit mean..."
    mean.append(stat.mean(hash48))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 64-bit mean..."
    mean.append(stat.mean(hash64))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 128-bit mean..."
    mean.append(stat.mean(hash128))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 160-bit mean..."
    mean.append(stat.mean(hash160))
    print("\t--- %s seconds ---" % (time.time() - start_time))

    # Calculate means difference.
    print "Calculating mean differences..."
    meanDiff.append(((mean[1] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[2] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[3] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[4] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[5] - mean[0]) / mean[0]) * 100)
    meanDiff.append(((mean[6] - mean[0]) / mean[0]) * 100)

    if errorType in ("stdev", "both"):
        std.extend(calculateSTD())
    if errorType in ("yerr", "both"):
        tmp1, tmp2 = calculateYerr()
        min_yerr.extend(tmp1)
        max_yerr.extend(tmp2)

    return (mean, meanDiff, std, min_yerr, max_yerr)


def calculateSTD():
    global start_time
    std = []

    print "Calculating standard deviations..."
    print "\tTLV standard deviation..."
    std.append(stat.stdev(tlv))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 16-bit standard deviation..."
    std.append(stat.stdev(hash16))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 32-bit standard deviation..."
    std.append(stat.stdev(hash32))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 48-bit standard deviation..."
    std.append(stat.stdev(hash48))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 64-bit standard deviation..."
    std.append(stat.stdev(hash64))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 128-bit standard deviation..."
    std.append(stat.stdev(hash128))
    print("\t--- %s seconds ---" % (time.time() - start_time))
    print "\tHash 160-bit standard deviation..."
    std.append(stat.stdev(hash160))
    print("\t--- %s seconds ---" % (time.time() - start_time))

    return std


def calculateYerr():
    min_yerr = []
    max_yerr = []

    print "Calculating y-axis error..."
    min_yerr.append(min(tlv))
    min_yerr.append(min(hash16))
    min_yerr.append(min(hash32))
    min_yerr.append(min(hash48))
    min_yerr.append(min(hash64))
    min_yerr.append(min(hash128))
    min_yerr.append(min(hash160))
    max_yerr.append(max(tlv))
    max_yerr.append(max(hash16))
    max_yerr.append(max(hash32))
    max_yerr.append(max(hash48))
    max_yerr.append(max(hash64))
    max_yerr.append(max(hash128))
    max_yerr.append(max(hash160))

    return (min_yerr, max_yerr)


if __name__ == "__main__":
    main(sys.argv[1:])
