import pyotp
import qrcode

img = qrcode.make(pyotp.totp.TOTP('JBSWY3DPEHPK3PXP').provisioning_uri(name='alice@google.com', issuer_name='Secure App'))
img.save("QR.png")

totp = pyotp.TOTP('JBSWY3DPEHPK3PXP')
print(totp.now())

# OTP verified for current time
print(totp.verify('492039'))
