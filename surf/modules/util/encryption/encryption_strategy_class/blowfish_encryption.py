import hashlib
from abc import ABC

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from surf.modules.util import EncryptionStrategy

class BlowfishEncryption(EncryptionStrategy, ABC):

    def __init__(self, key):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(key)
        self.key = sha256_hash.digest()

    def encrypt(self, data):
        cipher = Cipher(algorithms.AES(self.key), mode=modes.CFB(b'\x00' * 16), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext

    def decrypt(self, data):
        cipher = Cipher(algorithms.AES(self.key), mode=modes.CFB(b'\x00' * 16), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(data) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return unpadded_data
