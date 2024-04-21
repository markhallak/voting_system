from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta
import os

from pyasn1.type import univ, useful

from util.dilithiumAPI.DilithiumAPI import DilithiumAPI


def create_asn1_content(version, serial_number, signature_algorithm, issuer_name, validity_period, subject_name,
                        public_key):
    # This would normally involve constructing ASN.1 structure
    # Below is a highly simplified representation
    from pyasn1.type import univ, char, namedtype, tag

    class Certificate(univ.Sequence):
        componentType = namedtype.NamedTypes(
            namedtype.NamedType('version', univ.Integer()),
            namedtype.NamedType('serialNumber', univ.Integer()),
            namedtype.NamedType('signature', univ.ObjectIdentifier()),
            namedtype.NamedType('issuer', char.PrintableString()),
            namedtype.NamedType('validity', univ.Sequence(componentType=namedtype.NamedTypes(
                namedtype.NamedType('notBefore', useful.GeneralizedTime()),
                namedtype.NamedType('notAfter', useful.GeneralizedTime())
            ))),
            namedtype.NamedType('subject', char.PrintableString()),
            namedtype.NamedType('subjectPublicKeyInfo', univ.BitString())
        )


    cert = Certificate()
    cert['version'] = version
    cert['serialNumber'] = serial_number
    cert['signature'] = univ.ObjectIdentifier('1.3.6.1.4.1.12345.1')
    cert['issuer'] = issuer_name
    cert['validity']['notBefore'] = validity_period['not_before'].strftime("%Y%m%d%H%M%SZ")
    cert['validity']['notAfter'] = validity_period['not_after'].strftime("%Y%m%d%H%M%SZ")
    cert['subject'] = subject_name
    cert['subjectPublicKeyInfo'] = public_key

    return cert


def finalize_certificate_der(asn1_content, signature):
    from pyasn1.codec.der import encoder

    # Assuming signature is added as a direct component to the ASN.1 structure (this is simplified)
    asn1_content['signatureValue'] = univ.BitString(hexValue=signature.hex())

    # Encode the structure to DER
    der_encoded = encoder.encode(asn1_content)
    return der_encoded


def serialize_to_pem(der_encoded):
    import base64

    pem_encoded = base64.b64encode(der_encoded).decode('ascii')
    pem_certificate = f"-----BEGIN CERTIFICATE-----\n{pem_encoded}\n-----END CERTIFICATE-----"
    return pem_certificate.encode('ascii')


dilithium = DilithiumAPI()


# Manually create ASN.1 DER content
asn1_content = create_asn1_content(
    version=3,
    serial_number=x509.random_serial_number(),
    signature_algorithm="id-Dilithium3",
    issuer_name="CN=example.com CA",
    validity_period={"not_before": datetime.now(), "not_after": datetime.now() + timedelta(days=365)},
    subject_name="CN=example.com",
    public_key=dilithium.getPublicKey()
)

signature = dilithium.sign(asn1_content)

certificate_der = finalize_certificate_der(asn1_content, signature)
certificate_pem = serialize_to_pem(certificate_der)

with open('my_cert.pem', 'wb') as f:
    f.write(certificate_pem)
