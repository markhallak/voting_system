import base64
import os
from flask import Flask, render_template
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from util.kyberAPI.ccakem import kem_keygen1024, kem_encaps1024, kem_decaps1024

app = Flask(__name__, static_url_path="", static_folder="web/static", template_folder="web/templates")


def encrypt_data(key, plaintext):
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


def decrypt_data(key, encrypted_data):
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


def generateKeyPair():
    return kem_keygen1024()

def encapsulateSecret(publicKey):
    plainSharedSecret, cipherSharedSecret = kem_encaps1024(publicKey)
    # plainSharedSecretBytes = bytes([(x + 256) % 256 for x in plainSharedSecret])
    return plainSharedSecret, cipherSharedSecret


@app.route("/")
def home():
    private, public = generateKeyPair()
    plainSharedSecret, encapsulatedSharedSecret = encapsulateSecret(public)
    print(f"Plain Shared Secret: {plainSharedSecret}")
    print(f"Encapsulated Shared Secret: {encapsulatedSharedSecret}")
    # message = b"Hello, this is a secret message!"
    # encrypted_message = encrypt_data(plainSharedSecret, message)
    # decrypted_message = decrypt_data(plainSharedSecret, encrypted_message)
    # print("Decrypted Message:", decrypted_message.decode('utf-8'))
    print(f"Plain Shared Secret 2: {kem_decaps1024(private, encapsulatedSharedSecret)}")
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
