import sys
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac

backend = default_backend()

### HASH FUNCTIONS TO TRY
# 0. CRC16 (16 bits)
# 1. CRC32 (32 bits)
# 2. Siphash (64 bits)
# 3. MurmurHash (32 bits)
# 4. SHA256 (256 bits)

class Hasher(object):
    pass

class Encryptor(object):
    pass

class Obfuscator(object):
    def __init__(self):
        self.key = os.urandom(32)
        self.iv = os.urandom(16)

    def encrypt_cbc(self, blob):
        global backend
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(blob) + encryptor.finalize()
        return self.iv, ct, None

    def encrypt_cbc(self, blob):
        global backend
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(blob) + encryptor.finalize()
        return self.iv, ct, encryptor.tag

    def hash_hmac(self, blob):
        h = hmac.HMAC(self.key, hashes.SHA256(), backend=default_backend())
        h.update(blob)
        return h.finalize()

class URI(object):
    def __init__(self, uri_string, obfuscator):
        self.uri = uri_string.split("/")
        self.obfuscator = obfuscator

    def number_of_components(self):
        return len(self.uri)

    def obfuscate_encrypt_structured(self, index):
        ouri = self.uri[:index]
        for i in range(index, len(self.uri)):
            plaintext = self.uri[i]
            iv, ct, tag = self.obfuscator.encrypt_cbc(plaintext)
            ouri.append(ct)
        return ouri

    def obfuscate_encrypt_blob(self, index):
        plaintext = "/".join(self.uri[index:])
        iv, ct, tag = self.obfuscator.encrypt_cbc(plaintext)
        ouri = self.uri[:index] + [ct]
        return ouri

    def obfuscate_hash_structured(self, index):
        ouri = self.uri[:index]
        for i in range(index, len(self.uri)):
            plaintext = self.uri[i]
            ct = self.obfuscator.hash_hmac(plaintext)
            ouri.append(ct)
        return ouri

    def obfuscate_hash_blob(self, index):
        plaintext = "/".join(self.uri[index:])
        ct = self.obfuscator.hash_hmac(plaintext)
        ouri = self.uri[:index] + [ct]
        return ouri

    def __str__(self):
        return str(self.uri)

def main(args):
    if len(args) == 1:
        obfuscator = Obfuscator()
        uri = URI("/a/b/c", obfuscator)
        print uri

        ouri = uri.obfuscate_encrypt_blob(1)
        print ouri

        ouri = uri.obfuscate_encrypt_blob(2)
        print ouri

        ouri = uri.obfuscate_encrypt_blob(3)
        print ouri
    elif args > 1:
        obfuscator = Obfuscator()
        with open(args[1], "r") as fhandle:
            for line in fhandle:
                line = line.strip()
                uri = URI(line, obfuscator)

                for i in range(uri.number_of_components()):
                    ouri1 = uri.obfuscate_encrypt_blob(i)
                    ouri2 = uri.obfuscate_encrypt_structured(i)
                    ouri3 = uri.obfuscate_hash_blob(i)
                    ouri4 = uri.obfuscate_hash_structured(i)

                    print i, uri, ouri1, ouri2, ouri3, ouri4

if __name__ == "__main__":
    main(sys.argv)
