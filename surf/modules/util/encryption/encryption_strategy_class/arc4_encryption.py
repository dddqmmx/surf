import hashlib
from abc import ABC

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from surf.modules.util import EncryptionStrategy


class ARC4Encryption(EncryptionStrategy, ABC):

    def __init__(self, key):
        sha256_hash = hashlib.sha256()

        # 更新哈希对象以包含字节组
        sha256_hash.update(key)

        # 获取哈希值的十六进制表示
        self.key = sha256_hash.digest()

    def encrypt(self, data):
        # 使用ARC4算法，选择流模式而不是CBC模式
        cipher = Cipher(algorithms.ARC4(self.key), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()

        # 加密数据
        ciphertext = encryptor.update(data) + encryptor.finalize()

        return ciphertext

    def decrypt(self, data):
        # 使用ARC4算法，选择流模式而不是CBC模式
        cipher = Cipher(algorithms.ARC4(self.key), mode=None, backend=default_backend())
        decryptor = cipher.decryptor()

        # 解密数据
        decrypted_data = decryptor.update(data) + decryptor.finalize()

        return decrypted_data
