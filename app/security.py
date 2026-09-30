import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


# Password hashing using PBKDF2-HMAC-SHA256 with a unique random salt.
# The stored value contains the algorithm, iteration count, salt and digest.
PASSWORD_ITERATIONS = 310_000


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = stored_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = _b64decode(salt_text)
        expected_digest = _b64decode(digest_text)
        actual_digest = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt, iterations
        )
        return hmac.compare_digest(actual_digest, expected_digest)
    except (ValueError, TypeError):
        return False


def create_access_token(username: str) -> str:
    if ALGORITHM != "HS256":
        raise RuntimeError("This implementation requires HS256")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": username, "exp": int(expire.timestamp())}

    header_part = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    message = f"{header_part}.{payload_part}".encode("ascii")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_b64encode(signature)}"


def decode_access_token(token: str) -> str | None:
    try:
        header_part, payload_part, signature_part = token.split(".")
        header = json.loads(_b64decode(header_part))
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            return None

        message = f"{header_part}.{payload_part}".encode("ascii")
        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"), message, hashlib.sha256
        ).digest()
        supplied_signature = _b64decode(signature_part)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            return None

        payload = json.loads(_b64decode(payload_part))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None

        username = payload.get("sub")
        return username if isinstance(username, str) else None
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
