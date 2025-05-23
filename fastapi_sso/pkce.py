"""PKCE-related helper functions."""

import base64
import hashlib
import os


def get_code_verifier(length: int = 96) -> str:
    """Get code verifier for PKCE challenge."""
    length = max(43, min(length, 128))
    bytes_length = int(length * 3 / 4)
    return base64.urlsafe_b64encode(os.urandom(bytes_length)).decode("utf-8").replace("=", "")[:length]


def get_pkce_challenge_pair(verifier_length: int = 96) -> tuple[str, str]:
    """Get tuple of (verifier, challenge) for PKCE challenge."""
    code_verifier = get_code_verifier(verifier_length)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .replace("=", "")
    )

    return (code_verifier, code_challenge)
