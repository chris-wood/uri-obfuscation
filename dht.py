import math
import os
import os.path
import shutil

class DHT:
    def __init__(self, hashSize, numOfHT, path):
        self.hashSize = hashSize
        self.numOfHT = numOfHT

        # Calculate the hash table size.
        size = math.pow(2, hashSize) / numOfHT
        self.htSize = int(size)
        if int(size) != size:
            self.numOfHT = self.numOfHT + 1
            print "Adjusting number of hash tables to " + str(self.numOfHT)

        self.path = path
        # Create the hash table directory, first remove it if it exists.
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)

    # hashValue is in hex format.
    def insert(self, hashValue):
        htId = self._calculateHTId(hashValue)

        # Read the counter of the hash value.
        counter = self._read(hashValue)

        # If the hash value was found (i.e., counter > 0), copy the whole file
        # without this hash value.
        if counter > 0:
            self.__copyHT(htId, hashValue)

        # Append the hash with its correct counter. If the hash value is new,
        # counter at this point is 0, otherwise it will have a greater value. In
        # both cases, add 1 to the counter.
        self.__appendHT(htId, hashValue, counter + 1)


    def _read(self, hashValue):
        htId = self._calculateHTId(hashValue)

        counter = 0
        fileName = os.path.join(self.path, str(htId))
        # Open the file and look for the matching hashValue.
        if os.path.isfile(fileName):
            with open(fileName, "r") as htFile:
                for line in htFile:
                    lineChunks = line.split(":")
                    if lineChunks[0] == str(hashValue):
                        counter = int(lineChunks[1])
                        break

        return counter


    def _calculateHTId(self, hashValue):
        htId = int(hashValue / self.htSize) + 1
        # This throws and error if the htId is larger than number of hash tables.
        assert htId <= self.numOfHT
        return htId


    # Append hashValue to the end of htId hash table.
    def __appendHT(self, htId, hashValue, counter):
        fileName = os.path.join(self.path, str(htId))
        with open(fileName, "a+") as htFile:
            htFile.write(str(hashValue) + ":" + str(counter) + "\n")


    # Copy the specified htID hash table without the corresponding hashValue.
    def __copyHT(self, htId, hashValue):
        fileName = os.path.join(self.path, str(htId))
        tmpFileName = os.path.join(self.path, str(htId) + ".tmp")
        os.rename(fileName, tmpFileName)
        with open(tmpFileName, "r") as inFile:
            with open(fileName, "w+") as outFile:
                for line in inFile:
                    # Read line and ignore the same hashValue.
                    lineChunks = line.split(":")
                    if lineChunks[0] == str(hashValue):
                        continue

                    # Write line.
                    outFile.write(line)
        # Remove the tmp file.
        os.remove(tmpFileName)
