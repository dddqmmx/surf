from abc import abstractmethod, ABCMeta


class EncryptionStrategy(metaclass=ABCMeta):

    @abstractmethod
    def encrypt(self, data):
        pass

    @abstractmethod
    def decrypt(self, data):
        pass