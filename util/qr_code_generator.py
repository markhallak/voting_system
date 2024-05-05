import io
import pyotp
import qrcode
import base64
import secrets


class QRCodeGenerator:
    @staticmethod
    def generate_totp_secret():
        random_bytes = secrets.token_bytes(32)
        secret = base64.b32encode(random_bytes).decode('utf-8')
        return secret.replace('=', '')

    @staticmethod
    def generate_qr_code(name, secret):
        img = qrcode.make(
            pyotp.totp.TOTP(secret).provisioning_uri(name=name, issuer_name='Voting App'))

        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)

        return buf.getvalue()

    @staticmethod
    def verifyCode(secret, code):
        return pyotp.TOTP(secret).verify(code)
