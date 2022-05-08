import test
from test import toPower
import base64
from essential_generators import DocumentGenerator
from passlib import hash

def myPasswordEncrypt():
    password = input("Enter a password: ")
    password = password.encode("utf-8")
    encrypt1 = base64.b16encode(password)
    encrypt2 = base64.b32encode(password)
    encrypt3 = base64.b64encode(password)
    print("Password:", password)
    print("Encrypt 16:", encrypt1)
    print("Encrypt 32:", encrypt2)
    print("Encrypt 64:", encrypt3)

def securePassword():
    password = input("Enter a password: ")
    encrypt1 = hash.atlassian_pbkdf2_sha1.encrypt(password)
    encrypt2 = hash.sun_md5_crypt.encrypt(password)
    print("Password: ", password)
    print("Atlassian: ", encrypt1)
    print("Sun MD5: ", encrypt2)

securePassword()
securePassword()
securePassword()
