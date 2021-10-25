from cryptography.fernet import Fernet
from passlib.hash import argon2

class Hasher:
    def __init__(self, pepper_key):
        self.pepper = Fernet(pepper_key)

    def hash(self, pwd):
        hash = argon2.using(rounds=10).hash(pwd)
        hashb = hash.encode('utf-8')
        pep_hash = self.pepper.encrypt(hashb)
        return pep_hash

    def check(self, pwd, pep_hash):
        hashb = self.pepper.decrypt(pep_hash)
        hash = hashb.decode('utf-8')
        return argon2.verify(pwd, hash)

    @staticmethod
    def random_pepper():
        return Fernet.generate_key()
