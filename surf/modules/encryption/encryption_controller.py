from .encryption_strategy import EncryptionStrategy
from .models import BaseModel
# from models.aes_encryption import AESEncryption
# from models.arc4_encryption import ARC4Encryption
# from models.blowfish_encryption import BlowfishEncryption
# from surf.modules.util import TripleDESEncryption


class EncryptionController(EncryptionStrategy):

    def __init__(self, encrypted_information):
        self.encrypted_information = encrypted_information

    def create_encryption_strategy(self, info):
        encryption_type, encryption_key = info.split(':')
        encryption_key = encryption_key.encode('utf-8')
        if encryption_type == 'aes':
            return BaseModel(name="aes", abc=encryption_key)
            # return AESEncryption(encryption_key)
        elif encryption_type == 'blowfish':
            return BaseModel(name="blowfish", abc=encryption_key)
            # return BlowfishEncryption(encryption_key)
        elif encryption_type == 'triple_des':
            return BaseModel(name="triple_des", abc=encryption_key)
            # return TripleDESEncryption(encryption_key)
        elif encryption_type == 'arc4':
            return BaseModel(name="arc4", abc=encryption_key)
            # return ARC4Encryption(encryption_key)
        else:
            return None

    def encrypt(self, data):
        for info in self.encrypted_information:
            encryption_strategy = self.create_encryption_strategy(info)
            if encryption_strategy is not None:
                data = encryption_strategy.encrypt(data)
                print(data)
        return data

    def decrypt(self, data):
        for info in reversed(self.encrypted_information):
            encryption_strategy = self.create_encryption_strategy(info)
            if encryption_strategy is not None:
                data = encryption_strategy.decrypt(data)
                print(data)
        return data

if __name__ == '__main__':
    test_data = b'fuck you'
    encrypted_information = ['aes:AES的密码', "blowfish:Blowfish的密码", "triple_des:TripleDES的密码", "arc4:ARC4的密码"]
    encryption_controller = EncryptionController(encrypted_information)
    encrypt = encryption_controller.encrypt(test_data)
    print("114514", encrypt)
    print("1919810", encryption_controller.decrypt(encrypt))