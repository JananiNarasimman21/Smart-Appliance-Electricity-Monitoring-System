from __future__ import annotations

import ipaddress
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID


def collect_sans() -> list[x509.GeneralName]:
    names: list[x509.GeneralName] = [x509.DNSName("localhost")]
    names.append(x509.IPAddress(ipaddress.ip_address("127.0.0.1")))

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        ip_obj = ipaddress.ip_address(local_ip)
        names.append(x509.IPAddress(ip_obj))
    except Exception:
        pass

    # Add the user-shared LAN IP from the logs as a fallback for mobile.
    try:
        names.append(x509.IPAddress(ipaddress.ip_address("10.140.251.35")))
    except Exception:
        pass

    return names


def main() -> None:
    cert_path = Path("local-dev-cert.pem")
    key_path = Path("local-dev-key.pem")

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Local Dev"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )

    now = datetime.now(timezone.utc)

    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=825))
        .add_extension(x509.SubjectAlternativeName(collect_sans()), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
    )

    cert = cert_builder.sign(private_key=key, algorithm=hashes.SHA256())

    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    print(f"Wrote certificate: {cert_path.resolve()}")
    print(f"Wrote key: {key_path.resolve()}")


if __name__ == "__main__":
    main()
