import unittest
import dht
import os
import shutil
from collections import namedtuple


class DHTTest(unittest.TestCase):
    path = "dht_tmp"

    def test_insert(self):
        distributedHT = dht.DHT(8, 10, self.path)

        Case = namedtuple("Case", "hashValue htId counter")
        cases = [
            Case(5, 1, 1),
            Case(10, 1, 1),
            Case(5, 1, 2),
            Case(45, 2, 1),
            Case(110, 5, 1),
            Case(105, 5, 1),
            Case(110, 5, 2),
            Case(245, 10, 1),
            Case(252, 11, 1)
        ]

        for case in cases:
            self.assertEqual(distributedHT._calculateHTId(
                case.hashValue), case.htId)
            distributedHT.insert(case.hashValue)
            self.assertEqual(distributedHT._read(case.hashValue), case.counter)
            self.assertTrue(self.__ensureUniquness(case.hashValue, case.htId))

        # Cleaning up.
        shutil.rmtree(self.path, ignore_errors=True)


    # This function ensures that a hashValue is stored in htId and it is unique.
    def __ensureUniquness(self, hashValue, htId):
        fileName = os.path.join(self.path, str(htId))
        occurrence = 0
        with open(fileName, "r") as htFile:
            for line in htFile:
                lineChunks = line.split(":")
                if lineChunks[0] == str(hashValue):
                    occurrence = occurrence + 1

        return (occurrence == 1)


if __name__ == '__main__':
    unittest.main()
