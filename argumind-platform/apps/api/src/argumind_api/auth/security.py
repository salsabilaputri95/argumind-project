from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import struct
import time
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def _load_or_generate_rsa_keys() -> tuple[str, str]:
    priv_env = os.getenv("JWT_PRIVATE_KEY_PEM", "").strip()
    pub_env = os.getenv("JWT_PUBLIC_KEY_PEM", "").strip()
    if priv_env and pub_env:
        return priv_env, pub_env
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    pub_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    return priv_pem, pub_pem


PRIVATE_KEY_PEM, PUBLIC_KEY_PEM = _load_or_generate_rsa_keys()
ACCESS_TTL_SECONDS = 900
REFRESH_TTL_SECONDS = 7 * 24 * 3600


def hash_password(password: str) -> str:
    """Hash kata sandi menggunakan scrypt + salt acak 16-byte."""
    salt = secrets.token_hex(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt.encode("utf-8"), n=16384, r=8, p=1)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifikasi kata sandi secara constant-time."""
    try:
        salt, hex_digest = stored_hash.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt.encode("utf-8"), n=16384, r=8, p=1)
    return hmac.compare_digest(dk.hex(), hex_digest)


def create_jwt_token(
    user_id: str,
    role: str,
    org_id: str | None,
    token_type: str = "access",  # noqa: S107
    ttl_seconds: int = ACCESS_TTL_SECONDS,
) -> tuple[str, str]:
    """Buat JWT RS256 beserta ID unik jti."""
    jti = str(uuid.uuid4())
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "role": role,
        "org_id": org_id,
        "type": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    token = jwt.encode(payload, PRIVATE_KEY_PEM, algorithm="RS256")
    return token, jti


def decode_jwt_token(token: str) -> dict[str, str | int | None]:
    """Dekode dan verifikasi tanda tangan JWT RS256."""
    decoded: dict[str, str | int | None] = jwt.decode(token, PUBLIC_KEY_PEM, algorithms=["RS256"])
    return decoded


def generate_totp_code(secret_b32: str, for_time: int | None = None) -> str:
    """Generator kode TOTP 6-digit sesuai RFC 6238."""
    ts = int(time.time()) if for_time is None else for_time
    counter = ts // 30
    key = base64.b32decode(secret_b32.upper().strip(), casefold=True)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code_int:06d}"


def verify_totp_code(secret_b32: str, code: str, window: int = 1) -> bool:
    """Verifikasi kode TOTP dengan toleransi jendela waktu +/- 30 detik."""
    cleaned = code.strip()
    if len(cleaned) != 6 or not cleaned.isdigit():
        return False
    now = int(time.time())
    for delta in range(-window, window + 1):
        expected = generate_totp_code(secret_b32, for_time=now + (delta * 30))
        if hmac.compare_digest(expected, cleaned):
            return True
    return False
