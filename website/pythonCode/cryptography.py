from cryptography.hazmat.primitives.ciphers import algorithms, modes
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import random
import string

# generate a secure encryption key
def generate_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Encrypt the token
def encrypt_token(token: str, key: bytes) -> (bytes, bytes):
    iv = os.urandom(12)  
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    token_bytes = token.encode('utf-8')
    encrypted_token = encryptor.update(token_bytes) + encryptor.finalize()

    return encrypted_token, iv, encryptor.tag

# Decrypt the token
def decrypt_token(encrypted_token: bytes, key: bytes, iv: bytes, tag: bytes) -> str:
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_token = decryptor.update(encrypted_token) + decryptor.finalize()
    return decrypted_token.decode()

# Ejemplo de uso


if __name__ == "__main__":
    # contraseña aleatoria
    password = "".join(random.choice(string.ascii_letters) for i in range(16))
    print("Contraseña:", password)
    # Sal para derivar la clave (debe ser único y seguro)
    salt = os.urandom(16)
    # Generar la clave de cifrado
    key = generate_key(password, salt)

    # Token original
    token = "mi_token_secreto"

    # Cifrar el token
    encrypted_token, iv, tag = encrypt_token(token, key)
    print("Token cifrado:", encrypted_token)

    # Desencriptar el token
    decrypted_token = decrypt_token(encrypted_token, key, iv, tag)
    print("Token desencriptado:", decrypted_token)

