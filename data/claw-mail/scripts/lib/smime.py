"""S/MIME signing and encryption for outgoing emails.

This module provides helpers to:
- Sign an email with an S/MIME certificate (PKCS#12 or PEM)
- Encrypt an email to recipient certificates

Requires the ``cryptography`` library (``pip install cryptography``).

Usage::

    from lib.smime import SMIMESigner
    signer = SMIMESigner(cert_path="cert.pem", key_path="key.pem")
    signed_mime = signer.sign(mime_message)

    from lib.smime import SMIMEEncryptor
    encryptor = SMIMEEncryptor(recipient_certs=["recipient.pem"])
    encrypted_mime = encryptor.encrypt(mime_message)
"""

from __future__ import annotations

import logging
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from . import credential_store

logger = logging.getLogger("clawMail.smime")


class SMIMESigner:
    """Sign outgoing emails with an S/MIME certificate."""

    def __init__(
        self,
        cert_path: str = "",
        key_path: str = "",
        key_password: str | None = None,
        pkcs12_path: str = "",
        pkcs12_password: str | None = None,
    ) -> None:
        self.cert_path = cert_path
        self.key_path = key_path
        self.key_password = credential_store.resolve(key_password) if key_password else None
        self.pkcs12_path = pkcs12_path
        self.pkcs12_password = credential_store.resolve(pkcs12_password) if pkcs12_password else None
        self._cert = None
        self._key = None
        self._loaded = False

    def _load(self) -> None:
        """Load certificate and private key from PEM or PKCS#12 files."""
        if self._loaded:
            return

        try:
            from cryptography.hazmat.primitives.serialization import (
                load_pem_private_key,
                pkcs12,
            )
            from cryptography import x509
        except ImportError:
            raise ImportError(
                "S/MIME requires the 'cryptography' package. "
                "Install it with: pip install cryptography"
            )

        if self.pkcs12_path:
            with open(self.pkcs12_path, "rb") as f:
                p12_data = f.read()
            pwd = self.pkcs12_password.encode() if self.pkcs12_password else None
            self._key, self._cert, _ = pkcs12.load_key_and_certificates(p12_data, pwd)
        else:
            if self.cert_path:
                with open(self.cert_path, "rb") as f:
                    self._cert = x509.load_pem_x509_certificate(f.read())
            if self.key_path:
                with open(self.key_path, "rb") as f:
                    pwd = self.key_password.encode() if self.key_password else None
                    self._key = load_pem_private_key(f.read(), password=pwd)

        self._loaded = True

    def sign(self, mime_message: MIMEMultipart) -> MIMEMultipart:
        """Sign a MIME message, returning a multipart/signed wrapper.

        Creates an S/MIME signed message using PKCS#7 detached signature
        (application/pkcs7-signature).
        """
        self._load()

        try:
            from cryptography.hazmat.primitives.serialization import pkcs7, Encoding
            from cryptography.hazmat.primitives import hashes
        except ImportError:
            raise ImportError("S/MIME signing requires the 'cryptography' package.")

        if not self._key or not self._cert:
            raise ValueError("Both certificate and private key are required for signing")

        # Serialize the message to sign
        msg_bytes = mime_message.as_bytes()

        # Build PKCS#7 detached signature
        signature = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(msg_bytes)
            .add_signer(self._cert, self._key, hashes.SHA256())
            .sign(Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature])
        )

        # Build multipart/signed
        signed = MIMEMultipart(
            "signed",
            protocol="application/pkcs7-signature",
            micalg="sha-256",
        )
        signed.attach(mime_message)

        sig_part = MIMEApplication(signature, "pkcs7-signature", name="smime.p7s")
        sig_part.add_header("Content-Disposition", "attachment", filename="smime.p7s")
        signed.attach(sig_part)

        # Preserve original headers
        for hdr in ("From", "To", "Cc", "Subject", "Date", "Message-ID"):
            val = mime_message.get(hdr)
            if val and hdr not in signed:
                signed[hdr] = val

        return signed


class SMIMEEncryptor:
    """Encrypt outgoing emails to recipient S/MIME certificates."""

    def __init__(self, recipient_cert_paths: list[str] | None = None) -> None:
        self.recipient_cert_paths = recipient_cert_paths or []
        self._certs: list[Any] = []

    def _load_certs(self) -> None:
        if self._certs:
            return
        try:
            from cryptography import x509
        except ImportError:
            raise ImportError("S/MIME encryption requires the 'cryptography' package.")

        for path in self.recipient_cert_paths:
            with open(path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
                self._certs.append(cert)

    def encrypt(self, mime_message: MIMEMultipart) -> MIMEApplication:
        """Encrypt a MIME message to all recipient certificates.

        Returns an application/pkcs7-mime message.
        """
        self._load_certs()

        try:
            from cryptography.hazmat.primitives.serialization import pkcs7, Encoding
            from cryptography.hazmat.primitives.ciphers import algorithms
        except ImportError:
            raise ImportError("S/MIME encryption requires the 'cryptography' package.")

        if not self._certs:
            raise ValueError("At least one recipient certificate is required")

        msg_bytes = mime_message.as_bytes()

        builder = pkcs7.PKCS7EnvelopeBuilder().set_data(msg_bytes)
        for cert in self._certs:
            builder = builder.add_recipient(cert)

        encrypted = builder.encrypt(Encoding.DER, [])

        result = MIMEApplication(encrypted, "pkcs7-mime")
        result.set_param("smime-type", "enveloped-data")
        result.set_param("name", "smime.p7m")
        result.add_header("Content-Disposition", "attachment", filename="smime.p7m")

        # Preserve headers
        for hdr in ("From", "To", "Cc", "Subject", "Date", "Message-ID"):
            val = mime_message.get(hdr)
            if val:
                result[hdr] = val

        return result
