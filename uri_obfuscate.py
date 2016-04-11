import getopt
import sys
import time
import os
import os.path
import shutil
import obfuscate
import ntpath
from urlparse import urlparse


sizeUsed = ["16", "32", "48", "64", "128", "160"]
obfuscator = obfuscate.ObfuscatorSHA256()


def usage():
    print "python collision.py -i <inputPath> -o <outputPath>"
    print "                    -s <hashSize>"
    print ""
    print "\t-i, --ipath <inputPath>"
    print "\t\tis the path of a file containing the URI list, or a path to a"
    print "\t\tdirectory with a lot of files containing URI lists. If -p is"
    print "\t\tprovided, <inputPath> is the path of the output files to be"
    print "\t\tplotted."
    print "\t-o, --opath <outputPath>"
    print "\t\tis the path where obfuscated URIs will be stored. This path must"
    print "\t\tbe a directory."
    print "\t-s, --htype <hashSize>"
    print "\t\tis the size of the hash (obfuscation) function to use. Options:"
    print "\t\t'16', '32', '48', '64', '128', '160', or a comma separate list of"
    print "\t\tany of the previous values."


def main(argv):
    global start_time

    start_time = time.time()

    inputPath = ""
    outputPath = ""
    hashSize = ""
    try:
        opts, args = getopt.getopt(argv,"hi:o:pc:d:s:", ["help", "ipath=",
                                                         "opath=", "hsize="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--ipath"):
            inputPath = arg
        elif opt in ("-o", "--opath"):
            outputPath = arg
        elif opt in ("-s", "--hsize"):
            hashSize = arg
        else:
            usage()
            sys.exit(2)

    if inputPath == "":
        print "Missing input path."
        usage()
        sys.exit(2)

    if outputPath == "":
        print "Missing output path."
        usage()
        sys.exit(2)

    if hashSize == "":
        print "Missing hash size."
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

    # Prepare directories.
    if os.path.isdir(outputPath):
        shutil.rmtree(outputPath, ignore_errors=True)
    os.makedirs(outputPath)
    for size in sizes:
        os.makedirs(os.path.join(outputPath, str(size) + "-bit"))

    print "Processing input files..."
    if os.path.isfile(inputPath):
        processFile(inputPath, outputPath, sizes, ntpath.basename(inputPath))
    else:
        for fileName in [f for f in
                         sorted(os.listdir(inputPath)) if
                         os.path.isfile(os.path.join(inputPath, f))]:
            processFile(os.path.join(inputPath, f), outputPath, sizes, fileName)


def processFile(filePath, outputPath, sizes, fileName):
    global start_time

    print "\t'" + filePath + "'..."
    with open(filePath, "r") as inFile:
        # Open output files.
        outputFiles = {}
        for size in sizes:
            outputFiles[size] = open(os.path.join(outputPath,
                                                  str(size) + "-bit",
                                                  fileName), "w+")

        for line in inFile:
            components = strip_scheme(
                line.strip("\r").strip("\n")).split("/")

            # Calculating obfuscated names of all sizes,
            obfuscated= {}
            for size in sizes:
                obfuscated[size] = []
            for i in range(0, len(components)):
                name = "/" + "/".join(components[:i + 1])
                hashValue = obfuscator.obfuscate(name)
                for size in sizes:
                    obfuscated[size].append(hashValue[:((int(size) / 8) * 2)])

            # Save obfuscated names to output files.
            for size in sizes:
                outputFiles[size].write("/" + "/".join(obfuscated[size]) + "\n")

        # Close output files.
        for size in sizes:
            outputFiles[size].close()

    print("\t--- %s seconds ---" % (time.time() - start_time))


def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)


if __name__ == "__main__":
    main(sys.argv[1:])
