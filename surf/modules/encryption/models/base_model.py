# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/3/26 18:05
File Name       : base_model.py
Last Edit Time  : 
"""
from abc import ABC
from .aes_model import AESEncryption
from .arc4_model import ARC4Encryption
from .blowfish_model import BlowfishEncryption
from .triple_des_model import TripleDESEncryption


class BaseModel(ABC):

    def __init__(self, name, abc):
        self.setEncryptType(name)
        self.aes = AESEncryption(abc)
        self.arc4 = ARC4Encryption(abc)
        self.blowfish = BlowfishEncryption(abc)
        self.triple_des = TripleDESEncryption(abc)
        pass

    def setEncryptType(self, name="aes"):
        en_dict = {
            "aes": self.aes,
            "arc4": self.arc4,
            "blowfish": self.blowfish,
            "triple_des": self.triple_des,
        }
        name = 'aes' if name not in en_dict else name
        en_class = en_dict[name]
        for method_name in dir(en_class):
            if not method_name.startswith("__") and callable(getattr(en_class, method_name)):
                fn = getattr(en_class, method_name)
                setattr(self, method_name, fn)
        pass