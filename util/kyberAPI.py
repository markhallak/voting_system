import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from util.kyber.ccakem import kem_keygen1024, kem_encaps1024, kem_decaps1024


class KyberAPI:
    from cryptography.hazmat.primitives import padding

    def encrypt_data(self, plain_text, passphrase):
        # Convert the passphrase to bytes
        passphrase = passphrase.encode() if isinstance(passphrase, str) else passphrase

        # Convert plain_text to bytes and pad it
        padder = padding.PKCS7(128).padder()  # AES block size in bits
        plain_text = plain_text.encode() if isinstance(plain_text, str) else plain_text
        padded_data = padder.update(plain_text) + padder.finalize()

        # Generate a random salt and IV
        salt = os.urandom(16)
        iv = os.urandom(16)

        # Derive a key from the passphrase
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(passphrase)

        # Encrypt the padded data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded_data) + encryptor.finalize()

        # Combine salt, iv, and ciphertext, then Base64 encode
        encrypted = bytearray(salt + iv + ct)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_data(self, passphrase, encrypted_data):
        # Decode and prepare data
        passphrase = passphrase.encode() if isinstance(passphrase, str) else passphrase
        encrypted_data = base64.b64decode(encrypted_data)

        # Extract salt, iv, and ciphertext
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(passphrase)

        # Decrypt and remove padding
        # Decrypt the data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        try:
            return plaintext.decode('utf-8')
        except UnicodeDecodeError:  # Handle non-UTF8 plaintext
            return plaintext
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
print("Decrypted Message:", decrypted_message.decode('utf-8'))
