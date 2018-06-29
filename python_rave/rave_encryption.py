import base64
from Crypto.Cipher import DES3

class RaveEncryption(object):
    """ This is the class which handles Rave encryption. It is the superclass for all classes which implement encryption in this module """
    def __init__(self, encryptionKey):
        self.__encryptionKey = encryptionKey

    # Encryption for subclasses
    def _encrypt(self, plainText):
        """ This is the encryption function.\n
             Parameters include:\n 
            plainText (string) -- This is the text you wish to encrypt
        """
        blockSize = 8
        padDiff = blockSize - (len(plainText) % blockSize)
        cipher = DES3.new(self.__encryptionKey, DES3.MODE_ECB)
        plainText = "{}{}".format(plainText, "".join(chr(padDiff) * padDiff))
        encrypted = base64.b64encode(cipher.encrypt(plainText)).decode("utf-8")
        return encrypted
