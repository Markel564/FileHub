""" 
This modulue contains the functions to encrypt and decrypt a token using the AES-GCM algorithm.
"""

from cryptography.hazmat.primitives.ciphers import algorithms, modes
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import random
import string


def generate_key(password: str, salt: bytes):
    """ 
    input:
        - password: password to generate the key
        - salt: salt to generate the key
    output:
        - key: key to encrypt the token (in bytes)
    generatea a secure encryption key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), # we use the SHA256 algorithm
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend() 
    )
    return kdf.derive(password.encode()) # derive the key from the password

# Encrypt the token
def encrypt_token(token: str, key: bytes):
    """
    input:
        - token: token to encrypt
        - key: key to encrypt the token (obtained from the previous function)
    output:
        - encrypted_token: token encrypted
        - iv: initialization vector
        - tag: tag to verify the integrity of the token 
        (all in bytes)
    This function encrypts the token using the AES-GCM algorithm.

    """
    iv = os.urandom(12)   # Random Initialization vector
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()) # AES-GCM algorithm object
    encryptor = cipher.encryptor()  # Encryptor object
    token_bytes = token.encode('utf-8') # Convert the token to bytes
    encrypted_token = encryptor.update(token_bytes) + encryptor.finalize() # Encrypt the token

    return encrypted_token, iv, encryptor.tag


def decrypt_token(encrypted_token: bytes, key: bytes, iv: bytes, tag: bytes):
    """ 
    input:
        - encrypted_token: token encrypted
        - key: key to decrypt the token
        - iv: initialization vector
        - tag: tag to verify the integrity of the token
    output:
        - decrypted_token: token decrypted
    This function decrypts the token using the AES-GCM algorithm.
    """
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()) # AES-GCM algorithm object using tag and iv
    decryptor = cipher.decryptor() # Decryptor object
    decrypted_token = decryptor.update(encrypted_token) + decryptor.finalize() # Decrypt the token
    return decrypted_token.decode()

