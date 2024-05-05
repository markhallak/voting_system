import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from util.kyber.ccakem import kem_keygen1024, kem_encaps1024, kem_decaps1024


class KyberAPI:
    def encrypt_data(self, key, plaintext):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA3_512(),
            length=32,
            salt=salt,
            iterations=200000,
            backend=default_backend()
        )
        aes_key = kdf.derive(key)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return salt + iv + ct

    def decrypt_data(self, key, encrypted_data):
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ct = encrypted_data[32:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA3_512(),
            length=32,
            salt=salt,
            iterations=200000,
            backend=default_backend()
        )
        aes_key = kdf.derive(key)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext

    def decryptDataJS(self, encrypted_data_b64, passphrase):
        # Decode the base64 encoded data
        encrypted_data = base64.b64decode(encrypted_data_b64)

        # Extract the salt, iv and ciphertext from the combined byte array
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        # Derive the key using PBKDF2 HMAC with SHA-256
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )
        key = kdf.derive(passphrase.encode())

        # Decrypt the ciphertext using AES-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the plaintext
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode('utf-8')

    def generateKeyPair(self):
        return kem_keygen1024()

    def encapsulateSecret(self, publicKey):
        plainSharedSecret, cipherSharedSecret = kem_encaps1024(publicKey)
        plainSharedSecret = bytes([(x + 256) % 256 for x in plainSharedSecret])
        return plainSharedSecret, cipherSharedSecret


private, public = KyberAPI().generateKeyPair()
plainSharedSecret, encapsulatedSharedSecret = KyberAPI().encapsulateSecret(public)
print(f"Plain Shared Secret: {plainSharedSecret}")
print(f"Encapsulated Shared Secret: {encapsulatedSharedSecret}")
print(f"Plain Shared Secret 2: {kem_decaps1024(private, encapsulatedSharedSecret)}")

message = bytes("Hello, this is a secret message!".encode("utf-8"))
encrypted_message = KyberAPI().encrypt_data(plainSharedSecret, message)
print("Encrypted Message:", encrypted_message)
decrypted_message = KyberAPI().decrypt_data(plainSharedSecret, encrypted_message)
print("Decrypted Message:", decrypted_message.decode("utf-8"))
