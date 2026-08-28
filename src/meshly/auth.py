import hashlib
import hmac
import os


ITERATIONS = 310_000


def hash_password(password: str) -> tuple[str, str]:
    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )

    return (
        password_hash.hex(),
        salt.hex(),
    )


def verify_password(
    password: str,
    stored_hash: str,
    stored_salt: str,
) -> bool:

    salt = bytes.fromhex(stored_salt)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )

    return hmac.compare_digest(
        password_hash.hex(),
        stored_hash,
    )
