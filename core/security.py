import base64
import hashlib
import hmac
import secrets

from core.config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return "scrypt${}${}".format(
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, encoded: str | None) -> bool:
    if not encoded or not encoded.startswith("scrypt$"):
        return False
    try:
        _, encoded_salt, encoded_digest = encoded.split("$", 2)
        salt = base64.b64decode(encoded_salt)
        expected = base64.b64decode(encoded_digest)
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def session_secret() -> str:
    return get_settings().session_secret
