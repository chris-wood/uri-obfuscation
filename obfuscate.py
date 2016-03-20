import sys
import os
import getopt
import base64

import crc16
import binascii

import hashlib
import mmh3
import siphash

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac

backend = default_backend()

### "HASH" FUNCTIONS TO TRY
# DONE 0. CRC16 (16 bits)
# DONE 1. CRC32 (32 bits)
# DONE 2. Siphash (64 bits)
# DONE 3. MurmurHash (32 bits)
# DONE 4. SHA256 (256 bits)

class Obfuscator(object):
    def __init__(self, name):
        self.name = name

    def obfuscate(self, blob):
        pass # abstract

    def obfuscateDecimal(self, blob):
        pass # abstract

    def size(self):
        pass # abstract

    def __str__(self):
        return self.name


class ObfuscatorCRC16(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        return str(self.obfuscateDecimal(self, blob))

    def obfuscateDecimal(self, blob):
        crc = crc16.crc16xmodem(blob)
        return crc & 0xFFFF

    def size(self):
        return 16


class ObfuscatorCRC32(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        return str(self.obfuscateDecimal(self, blob))

    def obfuscateDecimal(self, blob):
        return binascii.crc32(blob) & 0xFFFFFFFF

    def size(self):
        return 32


class ObfuscatorMMH3(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        return str(self.obfuscateDecimal(self, blob))

    def obfuscateDecimal(self, blob):
        return mmh3.hash(blob) & 0xFFFFFFFF

    def size(self):
        return 32


class ObfuscatorMMH3_128(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        return str(self.obfuscateDecimal(self, blob))

    def obfuscateDecimal(self, blob):
        return mmh3.hash128(blob) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    def size(self):
        return 128


class ObfuscatorSipHash(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        return str(self.obfuscateDecimal(self, blob))

    def obfuscateDecimal(self, blob):
        key = '0123456789ABCDEF'
        sip = siphash.SipHash_2_4(key)
        sip.update(blob)
        return sip.hash() & 0xFFFFFFFFFFFFFFFF

    def size(self):
        return 64


class ObfuscatorSHA1(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        hasher = hashlib.new("sha1")
        hasher.update(blob)
        return hasher.hexdigest()

    def obfuscateDecimal(self, blob):
        return int(self.obfuscate(blob), 16)

    def size(self):
        return 160


class ObfuscatorSHA256(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        hasher = hashlib.new("sha256")
        hasher.update(blob)
        return hasher.hexdigest()

    def obfuscateDecimal(self, blob):
        return int(self.obfuscate(blob), 16)

    def size(self):
        return 256


class ObfuscatorHMAC(Obfuscator):
    def __init__(self):
        Obfuscator.__init__(self, self.__class__.__name__)
        self.key = os.urandom(32)

    def obfuscate(self, blob):
        h = hmac.HMAC(self.key, hashes.SHA256(), backend=default_backend())
        h.update(blob)
        return h.finalize()


class ObfuscatorAesCBC(Obfuscator):
    def __init__(self, key = "", iv = ""):
        Obfuscator.__init__(self, self.__class__.__name__)
        self.key = os.urandom(32)
        self.iv = os.urandom(16)

    def obfuscate(self, blob):
        global backend
        self.key = os.urandom(32)
        self.iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()

        BS = 16
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

        ct = encryptor.update(pad(blob)) + encryptor.finalize()
        return base64.b64encode("".join([self.iv, ct]))


class ObfuscatorAesGCM(Obfuscator):
    def __init__(self, key = "", iv = ""):
        Obfuscator.__init__(self, self.__class__.__name__)

    def obfuscate(self, blob):
        global backend
        self.key = os.urandom(32)
        self.iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(blob) + encryptor.finalize()
        return base64.b64encode("".join([self.iv, ct, encryptor.tag]))


class URI(object):
    def __init__(self, uri_string, obfuscator):
        self.uri = uri_string.split("/")
        self.obfuscator = obfuscator

    def number_of_components(self):
        return len(self.uri)

    def obfuscate(self, index):
        ouri = self.uri[:index]
        for i in range(index, len(self.uri)):
            plaintext = self.uri[i]
            ct = self.obfuscator.obfuscate(plaintext)
            ouri.append(ct)
        return ouri

    def obfuscate_flatten(self, index):
        plaintext = "/".join(self.uri[index:])
        ct = self.obfuscator.obfuscate(plaintext)
        ouri = self.uri[:index] + [ct]
        return ouri

    def __str__(self):
        return str(self.uri)


def obfuscate(lines, index, flatten, obfuscator):
    uris = [URI(line, obfuscator) for line in lines]
    mapped_uris = map(lambda u : u.obfuscate_flatten(index) if flatten else u.obfuscate(index), uris)
    #mapped_uris = map(lambda u : (u.obfuscate_flatten(index), u.obfuscate(index)), uris)
    output_uris = map(lambda u : "/".join(u), mapped_uris)
    #output_uris = map(lambda (u1, u2) : ("/".join(u1), "/".join(u2)), mapped_uris)

    return output_uris

def usage(args):
    print >> sys.stderr, "usage: python %s -a ALG -i [-f] INDEX" % (__name__)
    print >> sys.stderr, ""
    print >> sys.stderr, "   algorithms: CRC16 | CRC32 | MMH3 | SHA256 | AESGCM | AESCBC | SIPHASH"
    print >> sys.stderr, "   index:      the integer index after which obfuscation should be applied"
    print >> sys.stderr, "   flatten:    boolean indicating if the arguments should be flattened"
    sys.exit(-1)

def main(args):
    try:
        opts, args = getopt.getopt(args[1:], "a:i:d:fh", ["alg=", "datafile=", "index=", "flatten=", "help"])
    except getopt.GetoptError:
        usage(args)
        sys.exit(2)

    obfuscator_map = {
        "CRC16"   : ObfuscatorCRC16(),
        "CRC32"   : ObfuscatorCRC32(),
        "MMH3"    : ObfuscatorMMH3(),
        "SIPHASH" : ObfuscatorSipHash(),
        "SHA256"  : ObfuscatorSHA256(),
        "HMAC"    : ObfuscatorHMAC(),
        "AESCBC"  : ObfuscatorAesCBC(),
        "AESGCM"  : ObfuscatorAesGCM()
    }

    # sensible (?) defaults
    alg = "CRC16"
    flatten = False
    index = 0
    fromfile = False
    fname = ""

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(args)
            sys.exit()
        elif opt in ('-a', "--alg"):
            alg = arg
            if alg not in obfuscator_map:
                usage(args)
                sys.exit()
        elif opt in ('-i', '--index'):
            index = int(arg)
            if index < 1:
                usage(args)
                sys.exit()
        elif opt in ("-f", "--flatten"):
            flatten = True
        elif opt in ("-d", "--datafile"):
            fromfile = True
            fname = arg
            if not os.path.isfile(fname):
                usage(args)
                sys.exit()

    obfs = obfuscator_map[alg]
    if fromfile:
        with open(fname, "r") as fh:
            data = map(lambda l : l.strip(), fh.readlines())
            transformed = obfuscate(data, index, flatten, obfs)
            for t in transformed:
                print >> sys.stdout, t
    else:
        for line in sys.stdin.readlines():
            line = line.strip()
            transformed = obfuscate([line], index, flatten, obfs)
            print >> sys.stdout, transformed[0]

if __name__ == "__main__":
    main(sys.argv)
